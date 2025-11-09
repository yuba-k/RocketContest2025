import threading
import queue
import time

import motor
import imgProcess
import camera2

frame_q = queue.Queue(maxsize=1)
stop_event = threading.Event()

def start_camera(picam):
    i = 0
    while not stop_event.is_set():
        frame = picam.cap(cnt=i)
        i += 1
        try:
            if frame_q.full():
                frame_q.get_nowait(timeout = 0.1)
            frame_q.put_nowait(frame)
        except queue.Full:
            pass
        
def approach(mv):
    cmd = ""
    while not stop_event.is_set():
        try:
            frame = frame_q.get()
        except queue.Empty:
            continue
        cmd, _ = imgProcess.imgprocess(frame)
        if cmd == "goal":
            mv.adjust_duty_cycle("stop")
            print("ゴールしました")
            stop_event.set()
        mv.adjust_duty_cycle(cmd)

def main():
    picam = camera2.Camera()
    mv = motor.Motor()

    mv.adjust_duty_cycle("stop")
    try:
        threading.Thread(target=mv.move, daemon=True).start()
        threading.Thread(target=start_camera, args=(picam,) ,daemon=True).start()
        threading.Thread(target=approach,args=(mv,), daemon=True).start()
        while not stop_event.is_set():
            time.sleep(1)
    finally:
        mv.running = False
        stop_event.set()
        picam.disconnect()
        mv.cleanup()

if __name__ == "__main__":
    main()