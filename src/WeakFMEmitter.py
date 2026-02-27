import logging
import time

import RPi.GPIO
import smbus

import constants
import error

logger = logging.getLogger(__name__)


class FMemitter:
    def __init__(self):
        self.i2c = smbus.SMBus(1)
        self.addr = constants.VOICE_SYNTH_ADDR

    def _stringToAscii(self, message):
        string = [int(hex(ord(s)), 0) for s in message]
        return string

    def _sendDataViaI2C(self, string):
        try:
            self.i2c.write_i2c_block_data(self.addr, 0, string)
            time.sleep(1)
            self.i2c.write_byte_data(self.addr, 0, 0x0D)  # 終了コード
        except OSError as e:
            logger.error(f"OSerror:{e}")
        except error.FORCES_STOP:
            raise error.FORCES_STOP

    def transmitFMMessage(self, message):
        try:
            string = self._stringToAscii(message)
            self._sendDataViaI2C(string)
        except error.FORCES_STOP:
            raise error.FORCES_STOP

def main():
    fm = FMemitter()
    while True:
        string = input(">>>")
        fm.transmitFMMessage(string)


if __name__ == "__main__":
    main()
