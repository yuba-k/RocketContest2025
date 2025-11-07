import threading
import time

import motor
import imgProcess
import camera2

picam = camera2.Camera()
mv = motor.Motor()

running_flag = True
img = None

def start_motor():
    mv.move()

def start_camera():
    global img
    i = 0
    while running_flag:
        img = picam.cap(cnt=i)
        i += 1

def approach():
    cmd = ""
    while cmd != "goal":
        mv.direction = "stop"
        if img is not None:
            cmd, _ = imgProcess.imgprocess(img)
            mv.adjust_duty_cycle(cmd)
    mv.direction = "stop"
    mv.running = False
    print("ゴールしました")

def main():
    try:
        threading.Thread(target=start_motor,daemon=True).start()
        threading.Thread(target=start_camera,daemon=True).start()
        threading.Thread(target=approach,daemon=True).start()
        while True:
            time.sleep(1)
    finally:
        picam.disconnect()
        mv.cleanup()

if __name__ == "__main__":
    main()