"""this file is the sim of the hardware"""

import enum
import glob
import os
import struct
from time import sleep
import time
import numpy as np

# constants
FURL_MAX = 100
SHEET_FURL = 0
RUDDER_CENTER = 0
RECOVERY_COMM_INTERVAL = 10  # [seconds]
MAIN_SLEEP_INTERVAL = 0.1  # [ seconds]
PICTURE_INTERVAL = 10 * 60  # 10 minutes [seconds]


class Mode(enum.Enum):
    RECOVERY = 1
    MANUAL = 2
    AUTO = 3


class Timer:
    def __init__(self, duration):
        self.startns = None
        self.duration = duration

    def start(self):
        self.startns = time.time_ns()

    def is_done(self):
        return (
            self.startns is not None and time.time_ns() - self.startns >= self.duration
        )


# state
furl = None
sheet = None
rudder = None
slow_timer = Timer(10e9 * 10)  # 10 seconds # [nanoseconds]
fast_timer = Timer(10e8)  # .1 seconds # [nanoseconds]
comm_timer = Timer(RECOVERY_COMM_INTERVAL * 1e9)  # [nanoseconds]
picture_timer = Timer(PICTURE_INTERVAL * 1e9)
mode: Mode = Mode.RECOVERY
comm_id = 1
mission_id = 1

def set_furl(v):
    global furl
    furl = v


def get_furl():
    return furl


def set_sheet(v):
    global sheet
    sheet = v


def get_sheet():
    return sheet


def set_rudder(v):
    global rudder
    rudder = v


def get_rudder():
    return rudder


def get_att():
    # sim this as a 3 independent sinusoid t and derivatives
    # measurement error?
    t = time.time_ns()
    x = lambda t: np.sin(t)
    return x(t), x(t), x(t), x(t) - x(t - 1), x(t) - x(t - 1), x(t) - x(t - 1)


def get_wspd():
    return 5


def get_wdir():
    return 270


def get_compass():
    return 170


def get_temp():
    return 19


def get_humidity():
    return 19


def get_battery():
    return 19


def logfast(data):
    with open(
        os.path.abspath(os.path.join(__file__, "..", f"data-{comm_id:06d}.fast")),
        "ab",
    ) as f:
        f.write(data)


def logslow(data):
    with open(
        os.path.abspath(os.path.join(__file__, "..", f"data-{comm_id:06d}.slow")),
        "ab",
    ) as f:
        f.write(data)


def log_once():
    with open(
        os.path.abspath(os.path.join(__file__, "..", f"data-{comm_id:06d}.once")),
        "wb",
    ) as f:
        f.write(
            struct.pack(
                ">6IdI",
                mission_id,
                comm_id,
                FURL_MAX,
                SHEET_FURL,
                RUDDER_CENTER,
                RECOVERY_COMM_INTERVAL,
                MAIN_SLEEP_INTERVAL,
                PICTURE_INTERVAL,
            )
        )


def init():
    set_furl(FURL_MAX)
    set_sheet(SHEET_FURL)
    set_rudder(RUDDER_CENTER)
    slow_timer.start()
    fast_timer.start()
    comm_timer.start()
    picture_timer.start()


def main():
    global mode

    if mode == Mode.RECOVERY:
        mode = recoveryloop(mode)
    elif mode == Mode.MANUAL:
        pass
    elif mode == Mode.AUTO:
        pass

    sleep(MAIN_SLEEP_INTERVAL)


def take_picture():
    with open(
        os.path.abspath(os.path.join(__file__, "..", f"data-{comm_id:06d}.pic")),
        "ab",
    ) as f:
        f.write(b"\x00" * 640 * 480)


def recoveryloop(mode: Mode):
    # check furl motor
    set_furl(FURL_MAX)
    # check rudder
    set_rudder(RUDDER_CENTER)
    # compass
    # att
    if fast_timer.is_done():
        a = get_att()
        ws = get_wspd()
        wd = get_wdir()
        compass = get_compass()
        logfast(
            struct.pack(
                ">6f3f3f", *a, ws, wd, compass, get_furl(), get_sheet(), get_rudder()
            )
        )
        fast_timer.start()

    if slow_timer.is_done():
        logslow(struct.pack(">3f", get_temp(), get_humidity(), get_battery()))
        slow_timer.start()

    if picture_timer.is_done():
        take_picture()
        picture_timer.start()

    # comm
    if comm_timer.is_done():
        # gps
        mode = comm(mode)
        comm_timer.start()

    return mode


def comm(mode: Mode):
    global comm_id
    import requests

    log_once()

    files = {
        os.path.basename(f): f
        for f in glob.glob(
            os.path.abspath(os.path.join(__file__, "..", f"data-{comm_id:06d}.*"))
        )
    }
    # TODO clean up files once sent?
    try:
        resp = requests.post(
            "http://127.0.0.1:5000/telemetry",
            files=files,
            auth=("me", "password"),
        )
        if resp.text:
            # contents of command
            for line in resp.text:
                try:
                    command, args = line.split(":")
                    args = args.split(",")
                    if command == "changetomode":
                        if len(args) == 1:
                            mode = Mode(int(args[0]))
                    # if command == "setparam":
                    #     if len(args) == 2:
                except:
                    pass
        comm_id += 1
    except:
        pass

    return mode


if __name__ == "__main__":
    init()
    while True:
        main()