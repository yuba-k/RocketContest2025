import csv
import constants

import logging

logger = logging.getLogger(__name__)

def write(contents:list):
    try:
        with open(constants.GPS_LOG_PATH,"a") as f:
            writer = csv.writer(f)
            writer.writerow(contents)
    except FileNotFoundError:
        logging.warning("FileNotFoundError")