import camera2
import gpsnew
import motor
import imgProcess
import start
import error

import _thread
import time
from enum import Enum, auto

class state(Enum):
    STATE_INIT = auto()
    STATE_WAIT_DEPLOYMENT = auto()
    STATE_WAIT_GPS_FIX = auto()
    STATE_MOVE_BY_GPS = auto()
    STATE_MOVE_DIRECTION = auto()
    STATE_MOVE_PID = auto()
    STATE_GET_PHOTO = auto()
    STATE_TARGET_DETECTION = auto()
    STATE_JUDGE_GOAL = auto()
    STATE_JUDGE_GOAL = auto()


class flag():
    gyro_available = True
    camera_available = True

def forced_stop(runtime:int):
    fintime = time.time() + runtime
    while fintime - fintime > 0:
        time.sleep(10)
    _thread.interrupt_main()

def init():
    start.init()
    cm = camera2.Camera()
    try:
        mv = motor.Motor()
    except error.ERRROR_GYRO_INIT:
        flag.gyro_available = False
    
    gps = gpsnew.GPSModule()
    return cm, mv, gps

def main():
    cm, mv, gps = init()

    start.awaiting()

    # 強制終了命令を待機
    _thread.start_new_thread(forced_stop, (18*60))

if __name__ == "__main__":
    main()
