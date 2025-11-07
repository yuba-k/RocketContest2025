import RPi.GPIO as GPIO
import time

import configloading
import constants

class Motor():
    def __init__(self):
        config = configloading.Config_reader()
        self.duty = constants.DUTY
        self.right_pwm = constants.RIGHT_PWM
        self.left_pwm = constants.LEFT_PWM
        self.right_phase = constants.RIGHT_PHASE
        self.left_phase = constants.LEFT_PHASE

        GPIO.setmode(GPIO.BCM)#setmodeでBCMを用いて指定することを宣言　#GPIOピン番号のこと！

        self.direction = "stop"

        self.running = True

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
            self.right.ChangeDutyCycle(self.right_duty)
            self.left.ChangeDutyCycle(self.left_duty)
            time.sleep(0.05)

    def adjust_duty_cycle(self,direction):
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
            self.right.ChangeDutyCycle(0)
            self.left.ChangeDutyCycle(0)
        
    def cleanup(self):
        GPIO.cleanup()

def main():
    motor = Motor()
    print("forward,right,left")
    try:
        while True:
            direction =input("direction:")
            motor.move(direction,3,100)
    except KeyboardInterrupt:
        motor.cleanup()

if __name__ == "__main__":
    main()