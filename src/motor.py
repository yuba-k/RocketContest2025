import logging
import math
import threading
import time
from enum import Enum

import RPi.GPIO as GPIO

import configloading
import constants
import pid_controller

logger = logging.getLogger(__name__)


class ADJUST_DUTY_MODE(Enum):
    DIRECTION = 1
    ANGLE = 2


class Motor:
    def __init__(self, gyrosensor = None):
        config = configloading.Config_reader()
        self.duty = constants.DUTY
        self.baseduty = constants.BASE_DUTY
        self.right_pwm = constants.RIGHT_PWM
        self.left_pwm = constants.LEFT_PWM
        self.right_phase = constants.RIGHT_PHASE
        self.left_phase = constants.LEFT_PHASE

        self.gyroangle = gyrosensor
        self.pid = pid_controller.PID(kp=1.2, ki=0.2, kd=0.2, setpoint=0)

        GPIO.setmode(
            GPIO.BCM
        )  # setmodeでBCMを用いて指定することを宣言　#GPIOピン番号のこと！

        self.direction = "stop"

        self.running = True
        self.changeFlag = False
        self._lock = threading.Lock()
        self._stop_time = 0
        self._setup_gpio()

        self._initialize_motors()

    def _setup_gpio(self):
        GPIO.setup(self.right_pwm, GPIO.OUT)  # PWM出力
        GPIO.setup(self.right_phase, GPIO.OUT)  # デジタル出力
        GPIO.setup(self.left_pwm, GPIO.OUT)  # PWM出力
        GPIO.setup(self.left_phase, GPIO.OUT)  # デジタル出力

    def _initialize_motors(self):
        self.right = GPIO.PWM(self.right_pwm, 200)
        self.left = GPIO.PWM(self.left_pwm, 200)
        self.right.start(0)
        self.left.start(0)

    def move(self):
        GPIO.output(self.right_phase, GPIO.LOW)
        GPIO.output(self.left_phase, GPIO.LOW)
        while self.running:
            with self._lock:
                if time.time() > self._stop_time:
                    self._stop_time = 0
                    self.right_duty = self.left_duty = 0
                    self.changeFlag = True
            if self.changeFlag:
                self.changeFlag = False
                self.right.ChangeDutyCycle(self.right_duty)
                self.left.ChangeDutyCycle(self.left_duty)
            else:
                time.sleep(0.05)

    def adjust_duty_cycle(self, mode, direction=None, target_angle=0, sec=None):
        if mode == ADJUST_DUTY_MODE.DIRECTION:
            with self._lock:
                if sec is not None:
                    self._stop_time = time.time() + sec
            if direction == "forward":
                self.right_duty = self.duty
                self.left_duty = self.duty
            elif direction == "right" or direction == "search":
                self.right_duty = self.duty * 0.6
                self.left_duty = self.duty
            elif direction == "left":
                self.right_duty = self.duty * 1.0
                self.left_duty = self.duty * 0.6
            else:
                self.right_duty = self.left_duty = 0
            logger.info(f"Direction:{direction},Duty:{self.left_duty},{self.right_duty}")
            self.changeFlag = True
        elif mode == ADJUST_DUTY_MODE.ANGLE:
            count = 0
            current = time.monotonic()
            self.gyroangle.reset()
            self.pid.reset(setpoint=target_angle)
            logger.info(f"PID control is performed to achieve {target_angle}.")
            while time.monotonic() - current < sec:
                gyrodata = self.gyroangle.get_angle()
                pidout = self.pid.calc(gyrodata)
                self.right_duty = self.baseduty - pidout
                self.left_duty = self.baseduty + pidout
                self.changeFlag = True
                logger.debug(
                    f"Target:{target_angle},Gyro:{gyrodata},Duty:{self.right_duty},{self.left_duty}"
                )
                error = target_angle - gyrodata
                if abs(error) < 5:
                    count += 1
                    if count >5:
                        break
                time.sleep(0.05)
            self.right_duty = self.left_duty = 0
            self.changeFlag = True

    def cleanup(self):
        self.running = False
        if self.gyroangle is not None:
            self.gyroangle.stop()
        GPIO.cleanup()


def main():
    try:
        motor = Motor()
        threading.Thread(target=motor.move, daemon=True).start()
        while True:
            deg = int(input("DEGREE="))
            motor.adjust_duty_cycle(ADJUST_DUTY_MODE.ANGLE, target_angle=deg, sec=10)
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
    finally:
        motor.cleanup()


if __name__ == "__main__":
    main()
