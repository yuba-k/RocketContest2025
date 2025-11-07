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
    while running_flag:
        img = picam.cap()

def approach():
    cmd = ""
    i = 0
    while cmd != "goal":
        mv.direction = "stop"
        cmd, _ = imgProcess.imgprocess(img)
        mv.direction = cmd
        i += 1
    mv.direction = "stop"
    print("ゴールしました")

def main():
    try:
        threading.Thread(target=start_motor,daemon=True).start()
        threading.Thread(target=approach,daemon=True).start()
        threading.Thread(target=start_camera,daemon=True).start()
        while True:
            time.sleep(1)
    finally:
        picam.disconnect()
        mv.cleanup()

if __name__ == "__main__":
    main()