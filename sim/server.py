import sqlite3
import base64

from flask import Flask, request, g
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


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


# @app.route("/")
# def index():
#     return "Hello, World!"


@app.route("/telemetry", methods=["POST"])
def telemetry():
    if request.headers.get("Authorization"):
        auth = request.headers["Authorization"]
        if not auth.startswith("Basic "):
            return "Need basic auth", 401
        user, passw = (
            base64.b64decode(auth.replace("Basic ", "")).decode("utf-8").split(":")
        )
        if user != "me" or passw != app.config["BOAT_PASS"]:
            return "nice try", 401
        # else good
    else:
        return "Need basic auth", 401

    cur = get_db().cursor()
    cur.execute("insert into telemetry (raw) values (?);", request.get_data())

    # TODO parse the telemetry

    command = cur.execute("select (command) from command order date by limit 1;")

    return command, 200


if __name__ == "__main__":
    app.run()
