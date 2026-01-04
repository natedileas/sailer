from datetime import datetime
import os
import sqlite3
import base64

from flask import Flask, redirect, request, g, url_for
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE = "./db.sqlite"

app = Flask(__name__)
app.config.from_pyfile("config.py")


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource("schema.sql", mode="r") as f:
            db.cursor().executescript(f.read())
        db.commit()


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.route("/")
def index():
    return "Hello, World!"


# route ideas
# public
# /         project intro, info. latest thumbnail, map, etc
# /detail   latest, with command stream,
# /log/*      blog
@app.route("/log/")
def logs():
    fp = app.config["LOG_DIR"]
    return os.listdir(fp)


@app.route("/log/<entry>")
def log(entry):
    fp = os.path.join(app.config["LOG_DIR"], entry)
    if os.path.exists(fp):
        with open(fp, "r") as f:
            return f.read(), 200, {"Content-Type": "text/md"}
    else:
        return redirect(url_for("/"))


# private
# /cnc      like detail view, but with send command interface.


def auth():
    if request.headers.get("Authorization"):
        auth = request.headers["Authorization"]
        if not auth.startswith("Basic "):
            return False
        user, passw = (
            base64.b64decode(auth.replace("Basic ", "")).decode("utf-8").split(":")
        )
        if user != "me" or passw != app.config["BOAT_PASS"]:
            return False

        return True
    else:
        return False


@app.route("/command", methods=["POST"])
def command():
    if not auth():
        return "Need basic auth", 401
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "insert into command (dt, command) values (?,?);",
        (datetime.now().isoformat(), request.get_data()),
    )
    cur.close
    return "", 200


@app.route("/telemetry", methods=["POST"])
def telemetry():
    if not auth():
        return "Need basic auth", 401

    db = get_db()
    cur = db.cursor()
    cur.execute(
        "insert into telemetry (dt, raw) values (?,?);",
        (datetime.now().isoformat(), request.get_data()),
    )

    # TODO parse the telemetry, put it in dedicated tables (images, att, weather, etc)
    command = cur.execute(
        "select (command) from command order by dt limit 1;"
    ).fetchone()
    # TODO mark this command acted?
    cur.close()
    if not command:
        command = ""

    return command, 200


if __name__ == "__main__":
    init_db()
    app.run()
