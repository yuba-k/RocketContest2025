import time
import math
import threading

import logging

import board
import error
import constants
from adafruit_lsm6ds.lsm6ds33 import LSM6DS33
from adafruit_lsm6ds import Rate, GyroRange

logger = logging.getLogger(__name__)

class GYRO:
    def __init__(self, sample_rate=0.01):
        try:
            i2c = board.I2C()
            self.sensor = LSM6DS33(i2c,address=constants.IMU_ADDR)

            self._calibrate()
            self.sensor.gyro_data_rate = Rate.RATE_416_HZ
            self.sensor.gyro_range = GyroRange.RANGE_250_DPS

            self.alplha = 0.7
        except Exception as e:
            logger.critical("6軸初期化エラー")
            raise error.ERROR_GYRO_INIT from e

    def wrap_deg(self, x: float) -> float:
        # [-180, 180) に正規化
        return (x + 180.0) % 360.0 - 180.0

    def _calibrate(self, samples = 1000):
        total = 0.0
        for _ in range(samples):
            total += self.sensor.gyro[2]
            time.sleep(1/416)
        self.offset_z = math.degrees(total) / samples

    def _update_loop(self):
        last_time = time.perf_counter()
        while self.running:
            current_time = time.perf_counter()
            dt = current_time - last_time

            raw_z = math.degrees(self.sensor.gyro[2]) - self.offset_z
            self.filtered = self.alplha * raw_z + (1-self.alplha) * self.filtered
            self.gyro_z += self.filtered * dt
            
            last_time = current_time
            time.sleep(1/416)

    def get_angle(self):
        return self.wrap_deg(self.gyro_z)
    
    def start(self):
        self.gyro_z = 0.0
        self.filtered = 0.0
        self.running = True
#        self._calibrate()
        self.threadLoad = threading.Thread(target=self._update_loop, daemon=True)
        self.threadLoad.start()

    def stop(self):
        self.running = False
        self.threadLoad.join()

def main():
    try:
        gyro = GYRO()
        gyro.start()
        while True:
            gyro_z = gyro.get_angle()
            print(f"{gyro_z:3.3f}°")
            time.sleep(0.05)
    except Exception:
        if gyro is not None:
            gyro.stop()

if __name__ == "__main__":
    main()
