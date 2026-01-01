import camera2
import gpsnew
import motor
import imgProcess
import start
import error
import gyro_angle

import _thread
import time
from enum import Enum, auto
import logging

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
    try:
        cm = camera2.Camera()
    except error.ERROR_CAMERA_INIT as e:
        flag.camera_available = False
        logging.warning(f"縮退動作に移行します\n{e}")
    try:
        gyrosensor = gyro_angle.GYRO()
    except error.ERRROR_GYRO_INIT:
        flag.gyro_available = False
        logging.warning(f"縮退動作に移行します\n{e}")
    try:
        mv = motor.Motor(gyrosensor)
    except error.ERRROR_MOTOR_INIT:
        raise error.ERROR_MOTOR_INIT("モータの初期化に失敗しました")
    try:
        gps = gpsnew.GPSModule()
        gps.connect()
    except error.ERROR_GPS_CANNOT_CONNECTION:
        raise error.ERROR_GPS_CANNOT_CONNECTION("GPSセンサへの接続に失敗しました")
    return cm, mv, gps

def main():
    cm, mv, gps = init()

    start.awaiting()

    # 強制終了命令を待機
    _thread.start_new_thread(forced_stop, (18*60))

if __name__ == "__main__":
    main()
