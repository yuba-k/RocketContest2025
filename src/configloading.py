import configparser
import logging

logger = logging.getLogger()


class Config_reader:
    def __init__(self):
        try:
            self.config = configparser.ConfigParser()
            self.config.read("../config/cansat.ini", encoding="utf-8")
        except FileNotFoundError as e:
            logger.error(f"FIleNotFoudError\n{e}")

    def reader(self, key, value, style):
        var = self.config.get(key, value)
        if style == "intenger16":
            var = int(var, 0)
        elif style == "intenger":
            var = int(var)
        elif style == "character":
            var = str(var)
        elif style == "float":
            var = float(var)
        return var
