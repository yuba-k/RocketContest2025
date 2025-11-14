import threading
import queue
import time

import logging

import motor
import imgProcess
import camera2

frame_q = queue.Queue(maxsize=1)
stop_event = threading.Event()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

filehandler = logging.FileHandler("cansat.log")
filehandler.setLevel(logging.DEBUG)

consolehandler = logging.StreamHandler()
consolehandler.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s-%(filename)s-%(funcName)s-%(levelname)s-%(message)s")
filehandler.setFormatter(formatter)
consolehandler.setFormatter(formatter)

logger.addHandler(filehandler)
logger.addHandler(consolehandler)

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
        
def approach(mv, picam):
    cmd = ""
    cnt = 0
    while not stop_event.is_set():
        try:
            frame = frame_q.get()
        except queue.Empty:
            continue
        cmd, rs = imgProcess.imgprocess(frame)
        picam.save(rs,"../img/result/{cnt}test_cv2.jpg",camera2.RGB)
        if cmd == "goal":
            mv.adjust_duty_cycle("stop")
            logger.info("ゴールしました")
            stop_event.set()
        mv.adjust_duty_cycle(cmd)
        cnt += 1

def main():
    logger.info("CanSat起動")
    picam = camera2.Camera()
    mv = motor.Motor()
    logger.info("初期化完了")

    mv.adjust_duty_cycle("stop")
    try:
        threading.Thread(target=mv.move, daemon=True).start()
        threading.Thread(target=start_camera, args=(picam,) ,daemon=True).start()
        threading.Thread(target=approach,args=(mv,picam), daemon=True).start()
        logger.info("全スレッド起動")
        while not stop_event.is_set():
            time.sleep(1)
    finally:
        mv.running = False
        stop_event.set()
        picam.disconnect()
        mv.cleanup()
        logger.info("正常に終了しました")

if __name__ == "__main__":
    main()