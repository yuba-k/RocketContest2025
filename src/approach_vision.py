import logging
import logging.config
import queue
import threading
import time

import camera2
import imgProcess
import motor

frame_q = queue.Queue(maxsize=1)
stop_event = threading.Event()


def init_log():
    # ログの設定
    logging.config.fileConfig("../config/logconfig.ini")


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


def approach_long(mv, picam):
    cmd = ""
    while True:
        try:
            frame = frame_q.get()
        except queue.Empty:
            continue
        mv.adjust_duty_cycle(motor.ADJUST_DUTY_MODE.DIRECTION, "stop")
        cmd = imgProcess.detect_objects_long_range(frame)
        if cmd == "goal":
            return
        mv.adjust_duty_cycle(motor.ADJUST_DUTY_MODE.DIRECTION, cmd)


def approach_short(mv, picam):
    cmd = ""
    cnt = 0
    while not stop_event.is_set():
        try:
            frame = frame_q.get()
        except queue.Empty:
            continue
        cmd, rs = imgProcess.imgprocess(frame)
        picam.save(rs, "../img/result/{cnt}test_cv2.jpg", camera2.COLOR_MODE.RGB)
        if cmd == "goal":
            mv.adjust_duty_cycle(motor.ADJUST_DUTY_MODE.DIRECTION, "stop")
            logging.info("ゴールしました")
            stop_event.set()
        mv.adjust_duty_cycle(motor.ADJUST_DUTY_MODE.DIRECTION, cmd)
        cnt += 1


def main():
    init_log()
    logging.info("CanSat起動")
    picam = camera2.Camera()
    mv = motor.Motor()
    logging.info("初期化完了")

    # mv.adjust_duty_cycle(motor.ADJUST_DUTY_MODE,"stop")
    # logger.info("遠距離認識システム")
    # #カメラの起動
    # threading.Thread(target=start_camera, args=(picam,) ,daemon=True).start()
    # #モータの起動
    # threading.Thread(target=mv.move, daemon=True).start()
    # threadlong = threading.Thread(target=approach_long,args=(mv,picam),daemon=True)
    # threadlong.start()
    # threadlong.join()

    try:
        # カメラの起動
        threading.Thread(target=start_camera, args=(picam,), daemon=True).start()
        # モータの起動
        threading.Thread(target=mv.move, daemon=True).start()
        threading.Thread(target=approach_short, args=(mv, picam), daemon=True).start()
        logging.info("全スレッド起動")
        while not stop_event.is_set():
            time.sleep(1)
    finally:
        mv.running = False
        stop_event.set()
        picam.disconnect()
        mv.cleanup()
        logging.info("正常に終了しました")


if __name__ == "__main__":
    main()
