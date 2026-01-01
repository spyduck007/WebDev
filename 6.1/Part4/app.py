import sqlite3
from flask import Flask, render_template, request

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    conn = get_db_connection()
    heroes = conn.execute("SELECT c_id, c_name FROM characters").fetchall()
    conn.close()
    return render_template('index.html', heroes=heroes)


@app.route('/hero')
def hero():
    hero_id = request.args.get('id')

    conn = get_db_connection()
    hero = conn.execute(
        "SELECT * FROM characters WHERE c_id = ?",
        (hero_id,)
    ).fetchone()
    conn.close()

    return render_template('hero.html', hero=hero)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
