"""this file is the sim of the hardware"""

import enum
import os
from time import sleep
import time
import numpy as np

# constants
FURL_MAX = 100
SHEET_FURL = 0
RUDDER_CENTER = 0
RECOVERY_COMM_INTERVAL = 10  # [seconds]
MAIN_SLEEP_INTERVAL = 0.1  # [ seconds]


class Mode(enum.Enum):
    RECOVERY = 1
    MANUAL = 2
    AUTO = 3


# state
furl = None
sheet = None
rudder = None
timer = None
mode: Mode = Mode.RECOVERY


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


def set_timer(v):
    global timer
    timer = v


def get_timer():
    return timer


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


def log(data):
    with open(os.path.abspath(os.path.join(__file__, "..", "data.txt")), "a") as f:
        f.write(data)


def init():
    set_furl(FURL_MAX)
    set_sheet(SHEET_FURL)
    set_rudder(RUDDER_CENTER)
    set_timer(RECOVERY_COMM_INTERVAL)


def main():
    global mode

    while True:
        if mode == Mode.RECOVERY:
            mode = recoveryloop(mode)
        elif mode == Mode.MANUAL:
            pass
        elif mode == Mode.AUTO:
            pass

        sleep(MAIN_SLEEP_INTERVAL)


def recoveryloop(mode: Mode):
    # check furl motor
    set_furl(FURL_MAX)
    # check rudder
    set_rudder(RUDDER_CENTER)
    # compass
    # att
    a = get_att()
    # wspd
    ws = get_wspd()
    # wdir
    wd = get_wdir()
    log([a, ws, wd])

    # comm
    if get_timer() <= 0:
        # gps
        mode = comm(mode)
        set_timer(RECOVERY_COMM_INTERVAL)

    return mode


def comm(mode: Mode):
    import requests

    data = open(os.path.abspath(os.path.join(__file__, "..", "data.txt")), "r").read()
    resp = requests.post("http://192.168.0.1:5000/", data=data, auth=("me", "user"))
    if resp.text:
        # contents of command
        for line in resp.text:
            command, args = line.split(":")
            args = args.split(",")
            if command == "changetomode":
                if len(args) == 1:
                    mode = Mode(int(args[0]))

    return mode


