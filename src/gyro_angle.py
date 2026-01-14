import time
import math
import threading

import logging

import board
import error
from adafruit_lsm6ds.lsm6ds33 import LSM6DS33

logger = logging.getLogger()

class GYRO:
    def __init__(self, sample_rate=0.01):
        try:
            i2c = board.I2C()
            self.sensor = LSM6DS33(i2c)

            self.gyro_z = 0.0
            self.offset_z = 0.0
            self.sample_rate = sample_rate
            self.running = True

            self.recalibrate()

            self.thread = threading.Thread(target=self._update_loop, daemon=True)
            self.thread.start()
        except Exception as e:
            logger.critical("6軸初期化エラー")
            raise error.ERROR_GYRO_INIT from e


    def recalibrate(self, samples = 200):
        total = 0
        for _ in range(samples):
            total += self.sensor.gyro[2]
            time.sleep(0.005)
        self.offset_z = math.degrees(total) / samples

    def _update_loop(self):
        last_time = time.perf_counter()
        while self.running:
            current_time = time.perf_counter()
            dt = current_time - last_time

            raw_z = math.degrees(self.sensor.gyro[2]) - self.offset_z

            if abs(raw_z) < 0.005:
                raw_z = 0

            self.gyro_z += raw_z * dt
            
            last_time = current_time
            time.sleep(self.sample_rate)

    def get_angle(self):
        return self.gyro_z
    
    def reset(self):
        self.gyro_z = 0.0
        self.recalibrate()

    def stop(self):
        self.running = False

def main():
    gyro = GYRO()
    while True:
        gyro_z = gyro.get_angle()
        print(f"{gyro_z:3.3f}°")
        time.sleep(0.05)

if __name__ == "__main__":
    main()