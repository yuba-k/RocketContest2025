import logging
import threading
from enum import Enum
import error

import cv2
import numpy as np
from libcamera import controls
from picamera2 import Picamera2

import constants

logger = logging.getLogger(__name__)


class COLOR_MODE(Enum):
    RGB = 1
    BGR = 2


class Camera:
    def __init__(self):
        try:
            self.picam = Picamera2()
            self.picam.configure(
                self.picam.create_preview_configuration(
                    main={
                        "format": "RGB888",
                        "size": (constants.WIDTH, constants.HEIGHT),
                    }
                )
            )
            self.picam.set_controls(
                {
                    "AeConstraintMode": controls.AeConstraintModeEnum.Highlight,  # 露光モード：ハイライト
                    "AeExposureMode": controls.AeExposureModeEnum.Normal,  # 通常露光
                    "AeMeteringMode": controls.AeMeteringModeEnum.Matrix,  # 全体を考慮した測光
                }
            )
            self.picam.start()
        except Exception as e:
            logger.critical("カメラ初期化失敗")
            raise error.ERROR_CAMERA_INIT(f"カメラの初期化に失敗しました") from e

    def cap(self, cnt):
        try:
            im = self.picam.capture_array()
            im = cv2.flip(im, -1)
            self.save(im, f"../img/default/{cnt}test_cv2.jpg", COLOR_MODE.RGB)
            return im
        except Exception as e:
            logger.error(f"ImgSaveError:{e}")
            return None

    def save(self, im, fullpath, mode):
        if mode == COLOR_MODE.BGR:
            threading.Thread(
                target=cv2.imwrite, args=(fullpath, im), daemon=True
            ).start()
        elif mode == COLOR_MODE.RGB:
            im = cv2.cvtColor(im, cv2.COLOR_RGB2BGR)
            threading.Thread(
                target=cv2.imwrite, args=(fullpath, im), daemon=True
            ).start()

    def disconnect(self):
        self.picam.stop()
        self.picam.close()


def main():
    camera = Camera()
    camera.cap(900)


if __name__ == "__main__":
    main()
