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
    STRAIGHT = 3


class Motor:
    def __init__(self, gyrosensor = None, kp = constants.KP, ki = constants.KI, kd = constants.KD):
        config = configloading.Config_reader()
        self.duty = constants.DUTY
        self.baseduty = constants.BASE_DUTY
        self.right_pwm = constants.RIGHT_PWM
        self.left_pwm = constants.LEFT_PWM
        self.right_phase = constants.RIGHT_PHASE
        self.left_phase = constants.LEFT_PHASE

        self.gyroangle = gyrosensor
        self.pid = pid_controller.PID(kp, ki, kd, setpoint=0, limits=(-self.baseduty+10, self.baseduty-10))

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
                if time.monotonic() > self._stop_time:
                    self._stop_time = 0
                    self.right_duty = self.left_duty = 0
                    self.changeFlag = True
            if self.changeFlag:
                self.changeFlag = False
                self.right.ChangeDutyCycle(self.right_duty)
                self.left.ChangeDutyCycle(self.left_duty)
            else:
                time.sleep(0.05)

    def rotate_to_angle_pid(self, target_angle:float, sec:float, stable_count_threshold:int,stable_error:int):
        count = 0
        current = time.monotonic()
        self.gyroangle.reset()
        self.pid.reset(setpoint=target_angle)
        logger.info(f"PID control is performed to achieve {target_angle}.")
        with self._lock:
            if sec is not None:
                self._stop_time = current + sec
        print("time_set")
        while time.monotonic() < self._stop_time:
            gyrodata = self.gyroangle.get_angle()
            gyrodata = self.gyroangle.wrap_deg(gyrodata)#正規化-180<θ<180
            pidout = self.pid.calc(gyrodata)
            print(gyrodata, pidout)
            with self._lock:
                self.right_duty = self.baseduty - pidout
                self.left_duty = self.baseduty + pidout
                self.changeFlag = True
            logger.debug(
                f"Target:{target_angle},Gyro:{gyrodata},Duty:{self.right_duty},{self.left_duty}"
            )
            error = target_angle - gyrodata
            if abs(error) < stable_error:
                count += 1
                if count > stable_count_threshold:
                    self.right_duty = self.left_duty = 0
                    self.changeFlag = True
                    break
            else:
                count = 0
            time.sleep(0.02)


    def adjust_duty_cycle(self, mode, direction=None, target_angle=0, sec=None):
        if mode == ADJUST_DUTY_MODE.DIRECTION:
            with self._lock:
                if sec is not None:
                    self._stop_time = time.monotonic() + sec
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
            if sec < 4:
                raise ValueError(f"引数secが短すぎます:{sec}\nsecは4秒以上")
            count = 0
            div = target_angle / 90
            if div <= 1:
                self.rotate_to_angle_pid(target_angle, sec, stable_count_threshold = 5,stable_error=3)
            else:
                sec1, sec2 = 8, sec-4
                threshold1, threshold2 = 1, 5
                for dis_angle, sec, threshold, err in zip([90,target_angle-90],[sec1,sec2],[threshold1,threshold2],[5,3]):
                    print(dis_angle,sec,threshold)
                    self.rotate_to_angle_pid(dis_angle, sec, threshold,err)
        elif mode == ADJUST_DUTY_MODE.STRAIGHT:
            self.gyroangle.reset()
            self.pid.reset(setpoint=0) 
            with self._lock:
                if sec is not None:
                    self._stop_time = time.monotonic() + sec
            while time.monotonic() < self._stop_time:
                gyrodata = self.gyroangle.get_angle()
                correction = self.pid.calc(pid_controller.wrap_deg(gyrodata))
                
                with self._lock:
                    self.right_duty = self.baseduty - correction
                    self.left_duty = self.baseduty + correction
                    self.changeFlag = True
                    
                time.sleep(0.02)
            self.right_duty = self.left_duty = 0
            self.changeFlag = True

    def cleanup(self):
        self.running = False
        if self.gyroangle is not None:
            self.gyroangle.stop()
        GPIO.cleanup()


def main():
    import gyro_angle
    gyro = gyro_angle.GYRO()
    motor = None
    move_thread = None

    try:
        # PID入力
        pid_input = input("Enter Kp,Ki,Kd (or q to quit): ")
        if pid_input.lower() == "q":
            raise KeyboardInterrupt

        kp, ki, kd = map(float, pid_input.split(","))

        motor = Motor(gyrosensor=gyro, kp=kp, ki=ki, kd=kd)
        move_thread = threading.Thread(target=motor.move, daemon=True)
        move_thread.start()

        print("Motor started with PID:", kp, ki, kd)

        while True:
            cmd = input("Enter target angle (or 'q' to quit): ")

            if cmd.lower() == "q":
                raise KeyboardInterrupt

            try:
                target_angle = float(cmd)
            except ValueError:
                print("Invalid input")
                continue

            motor.adjust_duty_cycle(
                ADJUST_DUTY_MODE.ANGLE,
                target_angle=target_angle,
                sec=10
            )
           # time.sleep(5)

    except KeyboardInterrupt:
        print("\nStopping motor...")

    finally:
        if motor is not None:
            motor.cleanup()
        if gyro is not None:
            gyro.stop()
        print("Clean exit")
if __name__ == "__main__":
    main()
