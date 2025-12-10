import time

import board
from adafruit_lsm6ds.lsm6ds33 import LSM6DS33

i2c = board.I2C()
sensor = LSM6DS33(i2c)


class GYRO:
    def __init__(self):
        self.gyro_z = 0.0
        self._lasttime = None

    def get_data(self):
        """
        Returns:
            float: 弧度法で累積移動角を返値
        """
        if self._lasttime is None:
            self._lasttime = time.perf_counter()
            return 0.0
        currenttime = time.perf_counter()
        dt = currenttime - self._lasttime
        row_z = sensor.gyro[2]
        self.gyro_z += row_z * dt
        return self.gyro_z

    def reset(self):
        self.gyro_z = 0.0
        self._lasttime = None
