from datetime import datetime
import os
import sqlite3
import base64
import struct

from flask import Flask, redirect, render_template, request, g, url_for
import logging

# Configure logging before creating the app
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s",
)

DATABASE = os.path.abspath(os.path.join(__file__, "..", "db.sqlite"))

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
def close_db(error):
    """Closes the database again at the end of the request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/detail")
def detail():
    db = get_db()
    cur = db.cursor()
    (commwindowid,) = cur.execute(
        "select comm_id from once order by dt desc limit 1;"
    ).fetchone()
    slow = cur.execute(
        "select * from slow where comm_id=?;", (commwindowid,)
    ).fetchall()
    fast = cur.execute(
        "select * from fast where comm_id=?;", (commwindowid,)
    ).fetchall()
    once = cur.execute(
        "select * from once where comm_id=?;", (commwindowid,)
    ).fetchall()
    pic = cur.execute("select * from pics where comm_id=?;", (commwindowid,)).fetchall()
    db.close()
    return render_template(
        "detail.html", comm_id=commwindowid, slow=slow, fast=fast, once=once, pic=pic
    )

# route ideas
# public
# /         project intro, info. latest thumbnail, map, etc
# /detail   latest, with command stream, attittude, temp/pressure, etc
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
        return "Need basic auth", 401, {"WWW-Authenticate": "Basic realm='your mom'"}
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
    db.commit()

    # parse the telemetry, put it in dedicated tables (images, att, weather, etc)
    for fname, filecontent in request.files.items():
        comm_id = fname[5:11]
        root, filetype = os.path.splitext(fname)
        content = filecontent.stream.read()
        app.logger.debug("filetype: %s", filetype)
        app.logger.debug("content_type : %s", filecontent.content_type)
        app.logger.debug("content_length : %s", filecontent.content_length)
        app.logger.debug("headers : %s", filecontent.headers)
        app.logger.debug("unpacking content len: %s", len(content))
        if filetype == ".slow":
            for l in struct.iter_unpack(">3f", content):
                cur.execute(
                    "insert into slow (dt,comm_id,temp, humidity, battery) values (?,?,?,?,?);",
                    (datetime.now().isoformat(), comm_id, *l),
                )
        elif filetype == ".fast":
            for l in struct.iter_unpack(">6f3f3f", content):
                # *a, ws, wd, compass, get_furl(), get_sheet(), get_rudder()
                cur.execute(
                    "insert into fast (dt,comm_id,att_x,att_y,att_z,att_dx,att_dy,att_dz, wind_spd, wind_dir, compass, furl, sheet,rudder) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?);",
                    (datetime.now().isoformat(), comm_id, *l),
                )
        elif filetype == ".once":
            l = struct.unpack(">6IdI", content)
            cur.execute(
                "insert into once (dt, comm_id, mission_id, FURL_MAX, SHEET_FURL, RUDDER_CENTER, RECOVERY_COMM_INTERVAL, MAIN_SLEEP_INTERVAL, PICTURE_INTERVAL) values (?,?,?,?,?,?,?,?,?);",
                (datetime.now().isoformat(), comm_id, l[0], *l[2:]),
            )
        elif filetype == ".pic":
            base64png = content  # TODO decode and turn into web-ready
            cur.execute(
                "insert into pics (dt,comm_id,raw,base64) values (?,?,?,?);",
                (
                    datetime.now().isoformat(),
                    comm_id,
                    content,
                    base64png,
                ),
            )
    db.commit()

    command = cur.execute("select (command) from command order by dt asc;").fetchone()
    # TODO mark this command acted?
    cur.close()
    if not command:
        command = ""

    return command, 200


if __name__ == "__main__":
    init_db()
    app.run()
