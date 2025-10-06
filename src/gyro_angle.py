import time
import math

import board
from adafruit_lsm6ds.lsm6ds33 import LSM6DS33

i2c = board.I2C()
sensor = LSM6DS33(i2c)

print("3秒間の回転角度を計測します（X, Y, Z 軸）...")

# 積分用の初期化
angle_x = 0.0
angle_y = 0.0
angle_z = 0.0

duration = 3.0  # 計測時間（秒）
dt = 0.05       # サンプリング間隔（秒）
samples = int(duration / dt)

input("Enterで開始")#計測待機

for i in range(samples):
    gyro_x, gyro_y, gyro_z = sensor.gyro  # 単位: radians/s

    # 積分（角速度 × 時間間隔）
    angle_x += gyro_x * dt
    angle_y += gyro_y * dt
    angle_z += gyro_z * dt

    time.sleep(dt)

# ラジアン → 度 に変換
angle_x_deg = math.degrees(angle_x)
angle_y_deg = math.degrees(angle_y)
angle_z_deg = math.degrees(angle_z)

print(f"\n3秒間の回転角度:")
print(f"X軸: {angle_x_deg:.2f}°")
print(f"Y軸: {angle_y_deg:.2f}°")
print(f"Z軸: {angle_z_deg:.2f}°")