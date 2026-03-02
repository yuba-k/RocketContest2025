# -*- coding: utf-8 -*-
import logging
import time

import RPi.GPIO as GPIO

import constants

logger = logging.getLogger(__name__)

st_pin_out = constants.ST_PIN_OUT
st_pin_in = constants.ST_PIN_IN


def init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(st_pin_out, GPIO.OUT)
    GPIO.setup(st_pin_in, GPIO.IN)


def awaiting():
    GPIO.output(st_pin_out, GPIO.HIGH)
    while True:
        value = GPIO.input(st_pin_out)
        if value == 0:
            logger.info("Start Program")
            break
        time.sleep(1)
    GPIO.output(st_pin_out, GPIO.LOW)
    time.sleep(30)  # パラシュート展開後待機時間
    return
