# -*- coding: utf-8 -*-
import logging
import time

import RPi.GPIO as GPIO

import constants

logger = logging.getLogger(__name__)

st_pin = constants.ST_PIN


def init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(st_pin, GPIO.IN)


def awaiting():
    while True:
        value = GPIO.input(st_pin)
        if value == 0:
            logger.info("Start Program")
            break
        time.sleep(1)
    time.sleep(30)  # パラシュート展開後待機時間
    return
