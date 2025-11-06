import threading
import time

import motor
import imgProcess
import camera2

picam = camera2.Camera()
mv = motor.Motor()

def start_motor():
    mv.move()

def approach():
    cmd = ""
    i = 0
    while cmd != "goal":
        img = picam.cap(cnt=i)
        cmd, img = imgProcess.imgprocess(img)
        picam.save(img,i)
        mv.direction = cmd
        i += 1
    mv.direction = "stop"
    print("ゴールしました")

def main():
    try:
        threading.Thread(target=start_motor,daemon=True).start()
        threading.Thread(target=approach,daemon=True).start()
        while True:
            time.sleep(1)
    finally:
        picam.disconnect()
        mv.cleanup()

if __name__ == "__main__":
    main()