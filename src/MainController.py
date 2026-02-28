import _thread
import logging
import logging.config
import time
from enum import Enum, auto
import threading
import queue
import cv2

import camera2
import constants
import error
import gpsnew
import gyro_angle
import imgProcess
import motor
import start
import write_csv
import WeakFMEmitter


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
    fm_available = True
    waypoint_reached = False#中継地点到達の有無(T:到達済み/回り込まない，F:未到達/順光側経由)

frame_q = queue.Queue(maxsize=1)
save_q = queue.Queue(maxsize=10)
stop_event = threading.Event()

def forced_stop():
    time.sleep(constants.INTERRUPTED_TIME)
    _thread.interrupt_main()


def init():
    logging.config.fileConfig("../config/logconfig.ini", disable_existing_loggers=False)
    logging.info("初期化開始")
    start.init()
    try:
        cm = camera2.Camera()
    except error.ERROR_CAMERA_INIT as e:
        flag.camera_available = False
        cm = None
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
    try:
        fm = WeakFMEmitter.FMemitter()
    except Exception:
        flag.fm_available = False
        fm = None
    return cm, mv, gps, fm

def send_fm(fm,msg:str) -> None:
    try:
        if flag.fm_available:
            fm.transmitFMMessage(msg)
        else:
            pass
    except error.FORCED_STOP:
        raise error.FORCED_STOP

def save_worker():
    while not stop_event.is_set():
        im, fullpath = save_q.get()
        cv2.imwrite(fullpath, im)
        save_q.task_done()

def start_camera(picam):
    i = 0
    while not stop_event.is_set():
        frame = picam.cap(cnt=i)
        i += 1
        try:
            if frame_q.full():
                frame_q.get_nowait()
            frame_q.put_nowait(frame)
        except queue.Full:
            pass

def approach_short(mv, picam, fm):
    cmd = ""
    cnt = 0
    try:
        while not stop_event.is_set():
            #start = time.perf_counter()
            frame = None
            while not frame_q.empty():
                frame = frame_q.get_nowait()
            if frame is None:
                continue
            #st = time.perf_counter()
            cmd, rs = imgProcess.imgprocess(frame)
            #print(f"画像処理:{time.perf_counter()-st}")
            #st = time.perf_counter()
            save_q.put_nowait((rs, f"../img/result/{cnt}test_cv2.jpg"))
            #print(time.perf_counter()-st)
            if cmd == "goal":
                mv.adjust_duty_cycle(motor.ADJUST_DUTY_MODE.DIRECTION, "stop")
                logging.info("ゴールしました")
            #    send_fm(fm, "go-ru,simasita")
                stop_event.set()
            else:
                if cmd == "search":
            #        send_fm(fm, "sagasitemasu")
                    mv.adjust_duty_cycle(motor.ADJUST_DUTY_MODE.DIRECTION, "right")
                else:
                    send_fm(fm, "mituketa")
                    mv.adjust_duty_cycle(motor.ADJUST_DUTY_MODE.DIRECTION, cmd)
            cnt += 1
            #print(f"全体:{time.perf_counter()-start}")
    except error.FORCED_STOP:
        stop_event.set()
        raise error.FORCED_STOP
    except Exception:
        stop_event.set()
        return

def main():
    try:
        current_position = {"lat": 0.0, "lon": 0.0}
        past_position = {"lat": 0.0, "lon": 0.0}
        target_position = {"lat":0.0, "lon":0.0}
        goal_position = {"lat":constants.GOAL_LAT,"lon":constants.GOAL_LON}
        """順光側経由設定注意
        lat:緯度 / lon:経度
        午前中(太陽が東) -> lonを+0.000010(10m東)
        午後(太陽が西) -> lonを-0.000010(10m西)
        """
        relay_point = {"lat":constants.RELAY_LAT, "lon":constants.RELAY_LON}
        noimgcnt = 0
        imgcnt = 0
        cm = mv = gps = fm = None

        MISSION_START = None
        GOAL_REASON = ""

        NEXT_STATE = state.STATE_INIT
        while True:
            # if MISSION_START is not None:
            #     if time.monotonic() - MISSION_START > constants.INTERRUPTED_TIME:
            #         logging.info(f"{constants.INTERRUPTED_TIME}秒経過：強制ゴール判定")
            #         GOAL_REASON = "TIMEOUT"
            #         NEXT_STATE = state.STATE_GOAL
            # else:
            #     pass
            if NEXT_STATE == state.STATE_INIT:
                logging.info("STATE_INIT")
                try:
                    cm, mv, gps, fm = init()
                except error.ERROR_GPS_CANNOT_CONNECTION:
                    NEXT_STATE = state.ERROR
                    GOAL_REASON = "Failed to init gps"
                    continue
                except error.ERROR_MOTOR_INIT:
                    NEXT_STATE = state.ERROR
                    GOAL_REASON = "Failed to init motor"
                    continue
                if not(flag.waypoint_reached):#flag:Falsなら順光側経由
                    target_position = relay_point
                else:
                    target_position = goal_position
                logging.info(f"目標地点:{target_position}")
                NEXT_STATE = state.STATE_WAIT_DEPLOYMENT
            elif NEXT_STATE == state.STATE_WAIT_DEPLOYMENT:
                logging.info("STATE_WAIT_DEPLOYMENT")
                send_fm(fm, "taikityu-")
                start.awaiting()
                # ミッション開始時間を記録
                MISSION_START = time.monotonic()
                threading.Thread(target=forced_stop).start()
                # キャリア脱出
                threading.Thread(target=mv.move, daemon=True).start()
                logging.info("キャリア脱出")
                send_fm(fm,"zensin,simasu")
                if flag.gyro_available:
                    mv.adjust_duty_cycle(motor.ADJUST_DUTY_MODE.STRAIGHT, sec=(s := 10))
                else:
                    mv.adjust_duty_cycle(motor.ADJUST_DUTY_MODE.DIRECTION_TIME, "forward", sec=(s := 10))
                NEXT_STATE = state.STATE_TARGET_DETECTION
            elif NEXT_STATE == state.STATE_WAIT_GPS_FIX:
                logging.info("STATE_WAIT_GPS_FIX")
                while True:
                    send_fm(fm, "de-tasyutokutyu-")
                    lat, lon, satellites, utc_time, dop = gps.get_gps_data()
                    if lat is not None and lon is not None:
                        break
                    else:
                        logging.error("位置情報未受信")
                    send_fm(fm,"iti,syutokutyuu")
                logging.info(f"初期位置:{lat},{lon}\t{satellites},{utc_time},{dop}")
                write_csv.write([lat,lon,satellites,utc_time,dop,"1"])
                current_position = {"lat": lat, "lon": lon}
                if flag.gyro_available:
                    send_fm(fm, "zensin-")
                    mv.adjust_duty_cycle(motor.ADJUST_DUTY_MODE.STRAIGHT, sec=(s := 10))
                else:
                    mv.adjust_duty_cycle(motor.ADJUST_DUTY_MODE.DIRECTION_TIME, "forward", sec=(s := 10))
                NEXT_STATE = state.STATE_GET_GPS_DATA
            elif NEXT_STATE == state.STATE_GET_GPS_DATA:
                logging.info("STATE_GET_GPS_DATA")
                past_position = current_position.copy()
                while True:
                    send_fm(fm, "de-tasyutokutyu-")
                    lat, lon, satellites, utc_time, dop = gps.get_gps_data()
                    if lat is not None and lon is not None and gpsnew.is_correct(lat, lon, past_position):
                        break
                    else:
                        logging.error(f"上限値あるいは下限値を超過しています:{lat},{lon}")
                        write_csv.write([lat,lon,satellites,utc_time,dop,"0"])
                        time.sleep(1)
                logging.info(f"現在位置:{lat},{lon}\t{satellites},{utc_time},{dop}")
                write_csv.write([lat,lon,satellites,utc_time,dop,"1"])
                current_position = {"lat": lat, "lon": lon}
                calculate_result = gpsnew.calculate_target_distance_angle(
                    current_position, past_position, target_position, 10
                )
                logging.info(f"deg:{calculate_result['deg']}\tdis:{calculate_result['distance']}")
                if calculate_result["dir"] == "Immediate":
                    send_fm(fm, "mokuhyo-,toutyaku")
                    if not(flag.waypoint_reached):
                        logging.info("順光経由完了")
                        flag.waypoint_reached = True#順光側経由完了
                        target_position = goal_position#真のゴールへ
                    elif flag.camera_available:
                        NEXT_STATE = state.STATE_TARGET_DETECTION
                    else:
                        NEXT_STATE = state.STATE_GOAL
                        GOAL_REASON = "CameraDisavailable/EarlyTermination"
                elif flag.gyro_available:
                    NEXT_STATE = state.STATE_MOVE_PID
                else:
                    NEXT_STATE = state.STATE_MOVE_DIRECTION
            elif NEXT_STATE == state.STATE_MOVE_PID:
                logging.info("STATE_MOVE_PID")
                mv.adjust_duty_cycle(
                    motor.ADJUST_DUTY_MODE.ANGLE, target_angle=calculate_result["deg"], sec=(s := 8)
                )
                mv.adjust_duty_cycle(motor.ADJUST_DUTY_MODE.STRAIGHT, sec=(s := 10))
                NEXT_STATE = state.STATE_GET_GPS_DATA
            elif NEXT_STATE == state.STATE_MOVE_DIRECTION:
                logging.info("STATE_MOVE_DIRECTION")
                mv.adjust_duty_cycle(
                    motor.ADJUST_DUTY_MODE.DIRECTION,
                    calculate_result["dir"],
                    sec = (s := 4 * abs(calculate_result["deg"]) / 180),
                )
                NEXT_STATE = state.STATE_GET_GPS_DATA
            elif NEXT_STATE == state.STATE_TARGET_DETECTION:
                save_thread = threading.Thread(target=save_worker, daemon=True)
                save_thread.start()

                cam_thread = threading.Thread(target=start_camera, args=(cm,), daemon=True)
                cam_thread.start()

                imgdetect_thread = threading.Thread(target=approach_short, args=(mv, cm, fm), daemon=True)
                imgdetect_thread.start()
                
                save_thread.join()
                cam_thread.join()
                imgdetect_thread.join()
                GOAL_REASON = "SuccesufulAllPhase"
                NEXT_STATE = state.STATE_GOAL
            # elif NEXT_STATE == state.STATE_GET_PHOTO:
            #     logging.info("STATE_GET_PHOTO")
            #     img = cm.cap(imgcnt)
            #     imgcnt += 1
            #     NEXT_STATE = state.STATE_TARGET_DETECTION
            # elif NEXT_STATE == state.STATE_TARGET_DETECTION:
            #     logging.info("STATE_TARGET_DETECTION")
            #     dir, afimg = imgProcess.imgprocess(img)
            #     cm.save(afimg, f"../img/result/{imgcnt}afimg.jpg",camera2.COLOR_MODE.RGB)
            #     if dir == "goal":
            #         NEXT_STATE = state.STATE_GOAL
            #         GOAL_REASON = "SuccesufulAllPhase"
            #     elif dir == "search":
            #         if noimgcnt > 10:
            #             NEXT_STATE = state.STATE_WAIT_GPS_FIX
            #         else:
            #             noimgcnt += 1
            #             NEXT_STATE = state.STATE_MOVE
            #             dir = "right"
            #     else:
            #         NEXT_STATE = state.STATE_MOVE
            # elif NEXT_STATE == state.STATE_MOVE:
            #     logging.info("STATE_MOVE")
            #     if dir == "forward":
            #         if flag.gyro_available:
            #             mv.adjust_duty_cycle(motor.ADJUST_DUTY_MODE.STRAIGHT, sec=(s := 10))
            #         else:
            #             mv.adjust_duty_cycle(motor.ADJUST_DUTY_MODE.DIRECTION, "forward", sec=(s := 10))
            #     elif dir == "right" or dir == "left":
            #         mv.adjust_duty_cycle(
            #             motor.ADJUST_DUTY_MODE.DIRECTION, dir, sec = 4 * 45 / 180
            #         )
            #     elif dir == "search":
            #         mv.adjust_duty_cycle(
            #             motor.ADJUST_DUTY_MODE.DIRECTION, dir, sec = 4 * 60 / 180
            #         )
            #     NEXT_STATE = state.STATE_TARGET_DETECTION
            elif NEXT_STATE == state.ERROR:
                logging.info("ERROR")
                logging.critical("強制停止/異常によりプログラムを終了します")
                NEXT_STATE = state.STATE_GOAL
            elif NEXT_STATE == state.STATE_GOAL:
                logging.info("STATE_GOAL")
                logging.info(f"ゴール判定:{GOAL_REASON}")
                if cm is not None:
                    cm.disconnect()
                if mv is not None:
                    mv.cleanup()
                if gps is not None:
                    gps.disconnect()
                break
    except KeyboardInterrupt:
        GOAL_REASON = "FORCED STOP - TIMEOUT"
        logging.info(f"ゴール判定:{GOAL_REASON}")
    except error.FORCED_STOP:
        GOAL_REASON = "FORCED STOP - TIMEOUT"
        logging.info(f"ゴール判定")
    except Exception as e:
        logging.critical(f"エラーによる強制終了:{e}")
    finally:
            if cm is not None:
                cm.disconnect()
            if mv is not None:
                mv.cleanup()
            if gps is not None:
                gps.disconnect()

if __name__ == "__main__":
    main()
