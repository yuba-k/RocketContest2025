import RPi.GPIO as GPIO
import time
from enum import Enum
import threading
import math

import configloading
import constants
import gyro_angle
import pid_controller

class ADJUST_DUTY_MODE(Enum):
    DIRECTION = 1
    ANGLE = 2

class Motor():
    def __init__(self):
        config = configloading.Config_reader()
        self.duty = constants.DUTY
        self.baseduty = constants.BASE_DUTY
        self.right_pwm = constants.RIGHT_PWM
        self.left_pwm = constants.LEFT_PWM
        self.right_phase = constants.RIGHT_PHASE
        self.left_phase = constants.LEFT_PHASE

        self.gyroangle = gyro_angle.GYRO()
        self.pid = pid_controller.PID(kp=1.2,ki=0.2,kd=0.2,setpoint=0)

        GPIO.setmode(GPIO.BCM)#setmodeでBCMを用いて指定することを宣言　#GPIOピン番号のこと！

        self.direction = "stop"

        self.running = True
        self.changeFlag = False
        self.setup_gpio()

        self.initialize_motors()

    def setup_gpio(self):
        GPIO.setup(self.right_pwm,GPIO.OUT)#PWM出力
        GPIO.setup(self.right_phase,GPIO.OUT)#デジタル出力
        GPIO.setup(self.left_pwm,GPIO.OUT)#PWM出力
        GPIO.setup(self.left_phase,GPIO.OUT)#デジタル出力

    def initialize_motors(self):
        self.right = GPIO.PWM(self.right_pwm,200)
        self.left = GPIO.PWM(self.left_pwm,200)
        self.right.start(0)
        self.left.start(0)

    def move(self):
        GPIO.output(self.right_phase,GPIO.LOW)
        GPIO.output(self.left_phase,GPIO.LOW)
        while self.running:
            if self.changeFlag:
                self.changeFlag = False
                self.right.ChangeDutyCycle(self.right_duty)
                self.left.ChangeDutyCycle(self.left_duty)
            else:
                time.sleep(0.1)

    def adjust_duty_cycle(self,mode,direction=None,target_angle=None,sec=None):
        if mode == ADJUST_DUTY_MODE.DIRECTION:
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
            self.changeFlag = True
        elif mode == ADJUST_DUTY_MODE.ANGLE:
            current = time.time()
            self.pid.reset(setpoint=target_angle)
            while time.time() - current < sec:
                gyrodata = self.gyroangle.get_data()
                pidout = self.pid.calc(gyrodata)
                self.right_duty = self.baseduty - pidout
                self.left_duty = self.baseduty + pidout
                self.changeFlag = True
                time.sleep(1)
            self.right_duty = self.left_duty = 0
            self.gyroangle.reset()
            self.changeFlag = True
        
    def cleanup(self):
        GPIO.cleanup()

def main():
    try:
        motor = Motor()
        threading.Thread(target=motor.move,daemon=True).start()
        while True:
            deg = int(input("DEGREE="))
            deg = math.radians(deg)
            motor.adjust_duty_cycle(ADJUST_DUTY_MODE.ANGLE,target_angle=deg,sec=10)
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
    finally:
        motor.cleanup()          

if __name__ == "__main__":
    main()