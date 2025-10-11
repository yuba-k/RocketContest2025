import RPi.GPIO as GPIO
import time
import configloading
import board
from adafruit_lsm6ds.lsm6ds33 import LSM6DS33

import logwrite
import gyro_angle as gyro

class Motor():
    def __init__(self):
        self.config = configloading.Config_reader()
        self.log = logwrite.MyLogging()

        i2c = board.I2C()
        self.sensor = LSM6DS33(i2c)#ジャイロセンサ

        self.duty = self.config.reader("MOTOR","duty","intenger")
        self.right_pwm = self.config.reader("MOTOR","right_pwm","intenger")
        self.left_pwm = self.config.reader("MOTOR","left_pwm","intenger")
        self.right_phase = self.config.reader("MOTOR","right_phase","intenger")
        self.left_phase = self.config.reader("MOTOR","left_phase","intenger")

        GPIO.setmode(GPIO.BCM)#setmodeでBCMを用いて指定することを宣言　#GPIOピン番号のこと！

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
        # GPIO.output(self.right_phase,GPIO.HIGH)
        # GPIO.output(self.left_phase,GPIO.HIGH)
        self.right.start(0)
        self.left.start(0)

    def move(self,direction,degree,duty = None):
        if duty == None:
            duty = self.duty

        gyro_z = 0
        dt = 0.05

        self.adjust_duty_cycle(direction,duty)

        while True:
            gyro_z += self.sensor.gyro
            self.right.ChangeDutyCycle(self.right_duty)
            self.left.ChangeDutyCycle(self.left_duty)
            if(degree >= gyro_z):
                break
            time.sleep(dt)

        self.right.ChangeDutyCycle(0)
        self.left.ChangeDutyCycle(0)
        time.sleep(1)#オーバーヒート対策/位置情報信号

    def adjust_duty_cycle(self,direction,duty):
        GPIO.output(self.right_phase,GPIO.HIGH)
        GPIO.output(self.left_phase,GPIO.HIGH)
        if direction == "forward":
            self.log.write(f"forward,Duty:{duty}","INFO")
            self.right_duty = duty * 1.0
            self.left_duty = duty
        elif direction == "right" or direction == "search":
            self.log.write("right","INFO")
            self.right_duty = duty * 0.6
            self.left_duty = duty
        elif direction == "left":
            self.log.write("left","INFO")
            self.right_duty = duty * 1.0
            self.left_duty = duty * 0.6
        elif direction == "back":
            self.log.write("back","INFO")
            self.right_duty = self.left_duty = duty
            GPIO.output(self.right_phase,GPIO.LOW)
            GPIO.output(self.left_phase,GPIO.LOW)
        else:
            self.right_duty = self.left_duty = 0
        
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
