import time
import math
import threading

import board
from adafruit_lsm6ds.lsm6ds33 import LSM6DS33


class GYRO:
    def __init__(self, sample_rate=0.01):
        i2c = board.I2C()
        self.sensor = LSM6DS33(i2c)

        self.gyro_z = 0.0
        self.offset_z = 0.0
        self.sample_rate = sample_rate
        self.running = True

        self._calibrate()

        self.thread = threading.Thread(target=self._update_loop, daemon=True)
        self.thread.start()

    def _calibrate(self, samples = 200):
        total = 0
        for _ in range(samples):
            total += self.sensor.gyro[2]
            time.sleep(0.005)
        self.offset_z = total / samples

    def _update_loop(self):
        last_time = time.perf_counter()
        while self.running:
            current_time = time.perf_counter()
            df = current_time - last_time

            raw_z = self.sensor.gyro[2] - self.offset_z

            if abs(raw_z) < 0.005:
                raw_z = 0

            self.gyro_z += raw_z * dict
            
            last_time = current_time
            time.sleep(self.sample_rate)

    def get_angle(self):
        return self.gyro_z
    
    def reset(self):
        self.gyro_z = 0.0

    def stop(self):
        self.running = False