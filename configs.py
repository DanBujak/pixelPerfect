#!/usr/bin/python
import json

with open('settings.json') as settings_file:
    settings = json.load(settings_file)

BAUD = settings["serial"]["baud"]               # 800000 - Hard coded on STM32

WAKEUP_TIME = settings["clock"]["time"]["wakeup"]               # Hour to turn on each day (min 1)
SHUTDOWN_TIME = settings["clock"]["time"]["sleep"]            # Hour to turn off each day (max 2359)


# ---------------- Background colours and times --------------------

COLOR_AM = settings["clock"]["color"]["am"]
COLOR_NOON = settings["clock"]["color"]["noon"]
COLOR_PM = settings["clock"]["color"]["pm"]
COLOR_NIGHT = settings["clock"]["color"]["night"]
COLOR_OFF = settings["clock"]["color"]["black"]

TIME_AM = settings["clock"]["time"]["am"]
TIME_NOON = settings["clock"]["time"]["noon"]
TIME_PM = settings["clock"]["time"]["pm"]
TIME_NIGHT = settings["clock"]["time"]["night"]

STATE_CLOCK = 0
STATE_INSTAGRAM = 1
STATE_VISIBULL = 2
STATE_CUSTOM = 3
STATE_SHUTDOWN = 4

COLOUR_BLACK = settings["clock"]["color"]["black"]
