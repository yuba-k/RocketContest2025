import _thread
import logging
import logging.config
import time
from enum import Enum, auto
import threading

import camera2
import constants
import error
import gpsnew
import gyro_angle
import imgProcess
import motor
import start


class state(Enum):
    STATE_INIT = auto()
    STATE_WAIT_DEPLOYMENT = auto()
    STATE_WAIT_GPS_FIX = auto()
    STATE_GET_GPS_DATA = auto()
    STATE_MOVE_BY_GPS = auto()
    STATE_MOVE_DIRECTION = auto()
    STATE_MOVE_PID = auto()
    STATE_GET_PHOTO = auto()
    STATE_TARGET_DETECTION = auto()
    STATE_MOVE = auto()
    STATE_JUDGE_GOAL = auto()
    STATE_GOAL = auto()
    ERROR = auto()


class flag:
    gyro_available = True
    camera_available = True
    backlight_avoidance = True


def forced_stop(runtime: int):
    logging.info(f"強制終了命令をセット:{runtime}s")
    fintime = time.time() + runtime
    while fintime - time.time() > 0:
        time.sleep(10)
    _thread.interrupt_main()


def init():
    logging.config.fileConfig("../config/logconfig.ini", disable_existing_loggers=False)
    logging.info("初期化開始")
    start.init()
    try:
        cm = camera2.Camera()
    except error.ERROR_CAMERA_INIT as e:
        flag.camera_available = False
        logging.warning(f"縮退動作に移行します\n{e}")
    try:
        gyrosensor = gyro_angle.GYRO()
    except error.ERROR_GYRO_INIT as e:
        flag.gyro_available = False
        gyrosensor = None
        logging.warning(f"縮退動作に移行します\n{e}")
    try:
        mv = motor.Motor(gyrosensor)
    except error.ERROR_MOTOR_INIT:
        raise error.ERROR_MOTOR_INIT("モータの初期化に失敗しました")
    try:
        gps = gpsnew.GPSModule()
        gps.connect()
    except error.ERROR_GPS_CANNOT_CONNECTION:
        raise error.ERROR_GPS_CANNOT_CONNECTION("GPSセンサへの接続に失敗しました")
    return cm, mv, gps


def main():
    try:
        current_position = {"lat": 0.0, "lon": 0.0}
        past_position = {"lat": 0.0, "lon": 0.0}
        goal_position = {"lat":constants.GOAL_LAT,"lon":constants.GOAL_LON}
        relay_point = {"lat":constants.RELAY_LAT, "lon":constants.RELAY_LON}
        noimgcnt = 0
        imgcnt = 0

        MISSION_START = None
        GOAL_REASON = ""

        NEXT_STATE = state.STATE_INIT
        while True:
            if MISSION_START is not None:
                if time.monotonic() - MISSION_START > constants.INTERRUPTED_TIME:
                    logging.info(f"{constants.INTERRUPTED_TIME}秒経過：強制ゴール判定")
                    GOAL_REASON = "TIMEOUT"
                    NEXT_STATE = state.STATE_GOAL
            else:
                pass
            if NEXT_STATE == state.STATE_INIT:
                try:
                    cm, mv, gps = init()
                except error.ERROR_GPS_CANNOT_CONNECTION:
                    NEXT_STATE = state.ERROR
                    continue
                except error.ERROR_MOTOR_INIT:
                    NEXT_STATE = state.ERROR
                    continue
                NEXT_STATE = state.STATE_WAIT_DEPLOYMENT
            elif NEXT_STATE == state.STATE_WAIT_DEPLOYMENT:
                start.awaiting()
                # ミッション開始時間を記録
                MISSION_START = time.monotonic()
                # キャリア脱出
                threading.Thread(target=mv.move, daemon=True).start()
                logging.info("キャリア脱出")
                mv.adjust_duty_cycle(motor.ADJUST_DUTY_MODE.DIRECTION, "forward", sec=(s := 10))
                time.sleep(s + 2)
                NEXT_STATE = state.STATE_WAIT_GPS_FIX
            elif NEXT_STATE == state.STATE_WAIT_GPS_FIX:
                while True:
                    lat, lon, satellites, utc_time, dop = gps.get_gps_data()
                    if lat is not None and lon is not None:
                        break
                    else:
                        logging.error("位置情報未受信")
                logging.info(f"初期位置:{lat},{lon}\t{satellites},{utc_time},{dop}")
                current_position = {"lat": lat, "lon": lon}
                mv.adjust_duty_cycle(motor.ADJUST_DUTY_MODE.DIRECTION, "forward", sec=(s := 10))
                time.sleep(s + 2)
                NEXT_STATE = state.STATE_GET_GPS_DATA
            elif NEXT_STATE == state.STATE_GET_GPS_DATA:
                past_position = current_position.copy()
                while True:
                    lat, lon, satellites, utc_time, dop = gps.get_gps_data()
                    if lat is not None and lon is not None and gpsnew.is_correct(lat, lon, past_position):
                        break
                    else:
                        logging.error(f"上限値あるいは下限値を超過しています:{lat},{lon}")
                        time.sleep(1)
                logging.info(f"現在位置:{lat},{lon}\t{satellites},{utc_time},{dop}")
                current_position = {"lat": lat, "lon": lon}
                calculate_result = gpsnew.calculate_target_distance_angle(
                    current_position, past_position, goal_position, 10
                )
                if calculate_result["dir"] == "Immediate":
                    if flag.camera_available:
                        NEXT_STATE = state.STATE_GET_PHOTO
                    else:
                        NEXT_STATE = state.STATE_GOAL
                        GOAL_REASON = "CameraDisavailable/EarlyTermination"
                elif flag.gyro_available:
                    NEXT_STATE = state.STATE_MOVE_PID
                else:
                    NEXT_STATE = state.STATE_MOVE_DIRECTION
            elif NEXT_STATE == state.STATE_MOVE_PID:
                mv.adjust_duty_cycle(
                    motor.ADJUST_DUTY_MODE.ANGLE, target_angle=calculate_result["deg"], sec=(s := 8)
                )
                time.sleep(s + 2)
                NEXT_STATE = state.STATE_GET_GPS_DATA
            elif NEXT_STATE == state.STATE_MOVE_DIRECTION:
                mv.adjust_duty_cycle(
                    motor.ADJUST_DUTY_MODE.DIRECTION,
                    calculate_result["dir"],
                    sec = (s := 4 * abs(calculate_result["deg"]) / 180),
                )
                time.sleep(s + 2)
                NEXT_STATE = state.STATE_GET_GPS_DATA
            elif NEXT_STATE == state.STATE_GET_PHOTO:
                img = cm.cap(imgcnt)
                NEXT_STATE = state.STATE_TARGET_DETECTION
            elif NEXT_STATE == state.STATE_TARGET_DETECTION:
                dir, afimg = imgProcess.imgprocess(img)
                cm.save(afimg, f"../img/result/{imgcnt}afimg.jpg")
                if dir == "goal":
                    NEXT_STATE = state.STATE_GOAL
                    GOAL_REASON = "SuccesufulAllPhase"
                elif dir == "search":
                    if noimgcnt > 10:
                        NEXT_STATE = state.STATE_WAIT_GPS_FIX
                    else:
                        noimgcnt += 1
                        NEXT_STATE = state.STATE_MOVE
                        dir = "right"
                else:
                    NEXT_STATE = state.STATE_MOVE
            elif NEXT_STATE == state.STATE_MOVE:
                if dir == "forward":
                    mv.adjust_duty_cycle(motor.ADJUST_DUTY_MODE.DIRECTION, dir, sec = 8)
                elif dir == "right" or dir == "left":
                    mv.adjust_duty_cycle(
                        motor.ADJUST_DUTY_MODE.DIRECTION, dir, sec = 4 * 45 / 180
                    )
                elif dir == "search":
                    mv.adjust_duty_cycle(
                        motor.ADJUST_DUTY_MODE.DIRECTION, dir, sec = 4 * 60 / 180
                    )
                NEXT_STATE = state.STATE_TARGET_DETECTION
            elif NEXT_STATE == state.ERROR:
                logging.critical("強制停止/異常によりプログラムを終了します")
                NEXT_STATE = state.STATE_GOAL
            elif NEXT_STATE == state.STATE_GOAL:
                logging.info(f"ゴール判定:{GOAL_REASON}")
                cm.disconnect()
                mv.cleanup()
                gps.disconnect()
                break
    except Exception:
            cm.disconnect()
            mv.cleanup()
            gps.disconnect()
            logging.critical("エラーによる強制終了")

if __name__ == "__main__":
    main()
