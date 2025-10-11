from picamera2 import Picamera2
from libcamera import controls
import cv2
import numpy as np

import logwrite
import constants

class Camera():
    def __init__(self):
        try:
            self.log = logwrite.MyLogging()
            self.picam = Picamera2()
            self.picam.configure(self.picam.create_still_configuration(main={"format":"RGB888","size":(constants.WIDTH,constants.HEIGHT)}))
            self.picam.set_controls(
                {
                    "AeConstraintMode":controls.AeConstraintModeEnum.Highlight, #露光モード：ハイライト
                    "AeExposureMode": controls.AeExposureModeEnum.Normal,       # 通常露光
                    "AeMeteringMode": controls.AeMeteringModeEnum.Matrix        # 全体を考慮した測光
                }
            )

        except Exception as e:
            self.log.write("An error occurred during camera initialization","ERROR")
            raise
    def cap(self,cnt):
        try:
            self.picam.start()
            im = self.picam.capture_array()
            im = np.flipud(im)
            im = np.fliplr(im)
            self.save(im,cnt)
            return im
        except Exception as e:
            self.log.write("An error occurs when shooting","ERROR")
            return None
    def save(self,im,cnt):
        cv2.imwrite(f"../img/default/{cnt}test_cv2.jpg",im)
    def disconnect(self):
        self.picam.close()

def main():
    camera = Camera()
    camera.cap(900)

if __name__ == "__main__":
    main()
