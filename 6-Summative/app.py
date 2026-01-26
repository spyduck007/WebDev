from flask import Flask, render_template, request, redirect, url_for, session, g
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = "pokestay"
DB_PATH = "pokestay.db"


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS users
        (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            username       TEXT UNIQUE NOT NULL,
            password       TEXT        NOT NULL,
            display_name   TEXT,
            is_guest       INTEGER     NOT NULL DEFAULT 1,
            is_hotel_admin INTEGER     NOT NULL DEFAULT 0,
            is_site_admin  INTEGER     NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS hotels
        (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            description TEXT
        );

        CREATE TABLE IF NOT EXISTS rooms
        (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            hotel_id    INTEGER NOT NULL,
            room_number TEXT    NOT NULL,
            capacity    INTEGER NOT NULL,
            price       INTEGER NOT NULL,
            FOREIGN KEY (hotel_id) REFERENCES hotels (id),
            UNIQUE (hotel_id, room_number)
        );

        CREATE TABLE IF NOT EXISTS bookings
        (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id        INTEGER NOT NULL,
            room_id        INTEGER NOT NULL,
            check_in_date  TEXT    NOT NULL,
            check_out_date TEXT    NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (room_id) REFERENCES rooms (id)
        );
        """
    )

    hotel_count = db.execute("SELECT COUNT(*) FROM hotels").fetchone()[0]
    if hotel_count == 0:
        db.execute(
            "INSERT INTO hotels (name, description) VALUES (?, ?)",
            ("PokeCenter Kanto", "Kanto PokeCenter"),
        )
        db.execute(
            "INSERT INTO hotels (name, description) VALUES (?, ?)",
            ("PokeCenter Johto", "Johto PokeCenter"),
        )
        db.commit()

        kanto_id = db.execute(
            "SELECT id FROM hotels WHERE name = ?", ("PokeCenter Kanto",)
        ).fetchone()[0]
        johto_id = db.execute(
            "SELECT id FROM hotels WHERE name = ?", ("PokeCenter Johto",)
        ).fetchone()[0]

        rooms = [
            (kanto_id, "101", 2, 80),
            (kanto_id, "102", 3, 90),
            (kanto_id, "201", 4, 110),
            (johto_id, "1A", 2, 85),
            (johto_id, "2B", 3, 95),
            (johto_id, "3C", 4, 120),
        ]
        for r in rooms:
            db.execute(
                "INSERT INTO rooms (hotel_id, room_number, capacity, price) VALUES (?, ?, ?, ?)",
                r,
            )
        db.commit()

    user_count = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if user_count == 0:
        password = generate_password_hash("admin123")
        db.execute(
            "INSERT INTO users (username, password, display_name, is_guest, is_hotel_admin, is_site_admin) VALUES (?, ?, ?, ?, ?, ?)",
            ("admin", password, "Site Admin", 0, 0, 1),
        )
        db.commit()


with app.app_context():
    init_db()


@app.context_processor
def inject_user():
    user = None
    if "user_id" in session:
        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE id = ?", (session["user_id"],)
        ).fetchone()
    return {"current_user": user}


@app.route("/")
def index():
    db = get_db()
    hotels = db.execute("SELECT * FROM hotels").fetchall()
    return render_template("index.html", hotels=hotels)


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        display_name = request.form.get("display_name")
        password = request.form.get("password")
        if not username or not password:
            error = "Username and password are required."
        else:
            db = get_db()
            existing = db.execute(
                "SELECT id FROM users WHERE username = ?", (username,)
            ).fetchone()
            if existing:
                error = "Username already taken."
            else:
                pw_hash = generate_password_hash(password)
                db.execute(
                    "INSERT INTO users (username, password, display_name, is_guest, is_hotel_admin, is_site_admin) VALUES (?, ?, ?, ?, ?, ?)",
                    (username, pw_hash, display_name, 1, 0, 0),
                )
                db.commit()
                return redirect(url_for("login"))
    return render_template("register.html", error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            return redirect(url_for("index"))
        else:
            error = "Invalid username or password."
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/book", methods=["GET", "POST"])
def book():
    if "user_id" not in session:
        return redirect(url_for("login"))
    db = get_db()
    hotels = db.execute("SELECT * FROM hotels").fetchall()
    error = None
    if request.method == "POST":
        hotel_id = request.form.get("hotel_id")
        check_in = request.form.get("check_in")
        check_out = request.form.get("check_out")
        if not hotel_id or not check_in or not check_out:
            error = "Please fill in all fields."
            return render_template("book.html", hotels=hotels, error=error)
        rooms = db.execute(
            """
            SELECT r.id, r.room_number, r.price
            FROM rooms r
            WHERE r.hotel_id = ?
              AND r.id NOT IN (SELECT b.room_id
                               FROM bookings b
                               WHERE NOT (? <= b.check_in_date OR ? >= b.check_out_date))
            """,
            (hotel_id, check_in, check_out),
        ).fetchall()
        if not rooms:
            error = "No rooms available for those dates."
            return render_template("book.html", hotels=hotels, error=error)
        room = rooms[0]
        hotel = db.execute(
            "SELECT * FROM hotels WHERE id = ?", (hotel_id,)
        ).fetchone()
        return render_template(
            "confirm_booking.html",
            hotel=hotel,
            room=room,
            check_in=check_in,
            check_out=check_out,
        )
    return render_template("book.html", hotels=hotels, error=error)


@app.route("/confirm_booking", methods=["POST"])
def confirm_booking():
    if "user_id" not in session:
        return redirect(url_for("login"))
    hotel_id = request.form.get("hotel_id")
    room_id = request.form.get("room_id")
    check_in = request.form.get("check_in")
    check_out = request.form.get("check_out")
    if not hotel_id or not room_id or not check_in or not check_out:
        return redirect(url_for("book"))
    db = get_db()
    db.execute(
        "INSERT INTO bookings (user_id, room_id, check_in_date, check_out_date) VALUES (?, ?, ?, ?)",
        (session["user_id"], room_id, check_in, check_out),
    )
    db.commit()
    return redirect(url_for("booking_success"))


@app.route("/booking_success")
def booking_success():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("booking_success.html")


@app.route("/my_bookings")
def my_bookings():
    if "user_id" not in session:
        return redirect(url_for("login"))
    db = get_db()
    bookings = db.execute(
        """
        SELECT b.id,
               b.check_in_date,
               b.check_out_date,
               h.name AS hotel_name,
               r.room_number,
               r.price
        FROM bookings b
                 JOIN rooms r ON b.room_id = r.id
                 JOIN hotels h ON r.hotel_id = h.id
        WHERE b.user_id = ?
        ORDER BY b.check_in_date
        """,
        (session["user_id"],),
    ).fetchall()
    return render_template("my_bookings.html", bookings=bookings)


@app.route("/cancel_booking/<int:booking_id>", methods=["POST"])
def cancel_booking(booking_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    db = get_db()
    booking = db.execute(
        "SELECT * FROM bookings WHERE id = ? AND user_id = ?",
        (booking_id, session["user_id"]),
    ).fetchone()
    if booking:
        db.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
        db.commit()
    return redirect(url_for("my_bookings"))


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))
    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE id = ?", (session["user_id"],)
    ).fetchone()
    message = None
    if request.method == "POST":
        display_name = request.form.get("display_name")
        db.execute(
            "UPDATE users SET display_name = ? WHERE id = ?",
            (display_name, session["user_id"]),
        )
        db.commit()
        user = db.execute(
            "SELECT * FROM users WHERE id = ?", (session["user_id"],)
        ).fetchone()
        message = "Profile updated."
    return render_template("profile.html", user=user, message=message)


@app.route("/admin")
def admin():
    if "user_id" not in session:
        return redirect(url_for("login"))
    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE id = ?", (session["user_id"],)
    ).fetchone()
    if not user["is_site_admin"]:
        return redirect(url_for("index"))
    users = db.execute(
        "SELECT id, username, display_name, is_guest, is_hotel_admin, is_site_admin FROM users"
    ).fetchall()
    hotels = db.execute("SELECT * FROM hotels").fetchall()
    bookings = db.execute(
        """
        SELECT b.id,
               u.username,
               h.name AS hotel_name,
               r.room_number,
               b.check_in_date,
               b.check_out_date
        FROM bookings b
                 JOIN users u ON b.user_id = u.id
                 JOIN rooms r ON b.room_id = r.id
                 JOIN hotels h ON r.hotel_id = h.id
        ORDER BY b.check_in_date
        """
    ).fetchall()
    return render_template("admin.html", users=users, hotels=hotels, bookings=bookings)


if __name__ == "__main__":
    app.run(debug=True)
