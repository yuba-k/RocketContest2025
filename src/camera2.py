from picamera2 import Picamera2
from libcamera import controls
import cv2
import numpy as np
import threading
import logging
from enum import Enum

import constants

logger = logging.getLogger(__name__)

class COLOR_MODE(Enum) :
    RGB = 1
    BGR = 2

class Camera():
    def __init__(self):
        try:
            self.picam = Picamera2()
            self.picam.configure(self.picam.create_still_configuration(main={"format":"RGB888","size":(constants.WIDTH,constants.HEIGHT)}))
            self.picam.set_controls(
                {
                    "AeConstraintMode":controls.AeConstraintModeEnum.Highlight, #露光モード：ハイライト
                    "AeExposureMode": controls.AeExposureModeEnum.Normal,       # 通常露光
                    "AeMeteringMode": controls.AeMeteringModeEnum.Matrix        # 全体を考慮した測光
                }
            )
            self.picam.start()
        except Exception as e:
            threading.Thread(target=logger.error,args=(f"CameraError:{e}",))
            raise e
    def cap(self,cnt):
        try:
            im = self.picam.capture_array()
            im = cv2.flip(im,-1)
            self.save(im,"../img/default/{cnt}test_cv2.jpg",COLOR_MODE.RGB)
            return im
        except Exception as e:
            threading.Thread(target=logger.error(f"ImgSaveError:{e}",))
            return None
    def save(self,im,fullpath,mode):
        if mode == COLOR_MODE.BGR:
            threading.Thread(target = cv2.imwrite, args = (fullpath,im), daemon = True).start()
        elif mode == COLOR_MODE.RGB:
            im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
            threading.Thread(target = cv2.imwrite, args = (fullpath,im), daemon = True).start()
    def disconnect(self):
        self.picam.stop()
        self.picam.close()

def main():
    camera = Camera()
    camera.cap(900)

if __name__ == "__main__":
    main()
