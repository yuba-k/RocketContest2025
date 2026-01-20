import csv
import constants

def write(contents:list):
    with open(constants.GPS_LOG_PATH,"a") as f:
        writer = csv.writer(f)
        writer.writerow(contents)