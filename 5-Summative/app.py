from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import time

app = Flask(__name__)
app.secret_key = "secret-key"

TIME_LIMIT_SECONDS = 300


def get_time_info():
    if "start_time" not in session:
        return 0, 0
    elapsed = int(time.time() - session["start_time"])
    remaining = max(0, TIME_LIMIT_SECONDS - elapsed)
    return elapsed, remaining


def get_locks():
    locks = session.get("locks")
    if locks is None:
        locks = {
            "drawer": False,
            "door": False
        }
        session["locks"] = locks
    return locks


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            elapsed, remaining = get_time_info()
            return render_template(
                "index.html",
                error="Please type your name to start.",
                elapsed=elapsed,
                remaining=remaining,
                time_limit=TIME_LIMIT_SECONDS,
            )

        session.clear()
        session["player_name"] = name
        session["start_time"] = time.time()
        session["game_started"] = True
        session["locks"] = {
            "drawer": False,
            "door": False
        }
        return redirect(url_for("lab"))

    elapsed, remaining = get_time_info()
    return render_template(
        "index.html",
        error=None,
        elapsed=elapsed,
        remaining=remaining,
        time_limit=TIME_LIMIT_SECONDS,
        game_started=session.get("game_started", False),
    )


@app.route("/lab")
def lab():
    if "player_name" not in session:
        return redirect(url_for("index"))

    elapsed, remaining = get_time_info()
    if remaining <= 0:
        return redirect(url_for("game_over"))

    locks = get_locks()
    error = None
    if request.args.get("error") == "wrong_drawer":
        error = "That code didn't work. The drawer stays locked."

    return render_template(
        "lab.html",
        locks=locks,
        error=error,
        elapsed=elapsed,
        remaining=remaining,
        time_limit=TIME_LIMIT_SECONDS,
        game_started=session.get("game_started", False),
    )


@app.route("/unlock_drawer", methods=["POST"])
def unlock_drawer():
    if "player_name" not in session:
        return redirect(url_for("index"))

    elapsed, remaining = get_time_info()
    if remaining <= 0:
        return redirect(url_for("game_over"))

    code = request.form.get("drawer_code", "").strip().lower()
    if code == "retro":
        locks = get_locks()
        locks["drawer"] = True
        session["locks"] = locks
        return redirect(url_for("lab"))
    else:
        return redirect(url_for("lab", error="wrong_drawer"))


@app.route("/hallway")
def hallway():
    if "player_name" not in session:
        return redirect(url_for("index"))

    elapsed, remaining = get_time_info()
    if remaining <= 0:
        return redirect(url_for("game_over"))

    locks = get_locks()
    if not locks.get("drawer"):
        return redirect(url_for("lab"))

    error = None
    if request.args.get("error") == "wrong_door":
        error = "The lock beeps angrily. Wrong number."

    return render_template(
        "hallway.html",
        locks=locks,
        error=error,
        elapsed=elapsed,
        remaining=remaining,
        time_limit=TIME_LIMIT_SECONDS,
        game_started=session.get("game_started", False),
    )


@app.route("/door_lock", methods=["POST"])
def door_lock():
    if "player_name" not in session:
        return redirect(url_for("index"))

    elapsed, remaining = get_time_info()
    if remaining <= 0:
        return redirect(url_for("game_over"))

    locks = get_locks()
    if not locks.get("drawer"):
        return redirect(url_for("lab"))

    code = request.form.get("door_code", "").strip()
    if code == "4531":
        locks["door"] = True
        session["locks"] = locks
        return redirect(url_for("vault"))
    else:
        return redirect(url_for("hallway", error="wrong_door"))


@app.route("/vault")
def vault():
    if "player_name" not in session:
        return redirect(url_for("index"))

    elapsed, remaining = get_time_info()
    if remaining <= 0:
        return redirect(url_for("game_over"))

    locks = get_locks()
    if not locks.get("door"):
        return redirect(url_for("hallway"))

    return render_template(
        "vault.html",
        elapsed=elapsed,
        remaining=remaining,
        time_limit=TIME_LIMIT_SECONDS,
        game_started=session.get("game_started", False),
    )


@app.route("/game_over")
def game_over():
    elapsed, remaining = get_time_info()
    return render_template(
        "game_over.html",
        elapsed=elapsed,
        remaining=remaining,
        time_limit=TIME_LIMIT_SECONDS,
        game_started=session.get("game_started", False),
    )


@app.route("/time_status")
def time_status():
    elapsed, remaining = get_time_info()
    return jsonify(
        {
            "elapsed": elapsed,
            "remaining": remaining,
            "limit": TIME_LIMIT_SECONDS,
        }
    )


@app.route("/reset")
def reset():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
