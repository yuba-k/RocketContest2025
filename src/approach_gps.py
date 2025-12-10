import logging
import logging.config
import threading
import time

import constants
import gpsnew
import motor

gps = None
mv = None

logger = logging.getLogger(__name__)
logging.config.fileConfig("../config/logconfig.ini")


def init():
    global gps, mv
    gps = gpsnew.GPSModule()
    mv = motor.Motor()
    gps.connect()


def gps_movement(target, current_coordinate, target_distance):
    while True:
        previous_coordinate = current_coordinate.copy()
        while True:
            lat, lon, satellites, utc_time, dop = gps.get_gps_data()
            if gpsnew.cheak_data(lat, lon, previous_coordinate):
                break
            else:
                time.sleep(1)
        current_coordinate = {"lat": lat, "lon": lon}
        result = gpsnew.calculate_target_distance_angle(
            current_coordinate, previous_coordinate, target, target_distance
        )
        match result["dir"]:
            case "Immediate":
                return current_coordinate
            case "forward":
                pass
            case "left":
                mv.adjust_duty_cycle(
                    motor.ADJUST_DUTY_MODE.ANGLE, target_angle=result["degree"], sec=4
                )
            case "right":
                mv.adjust_duty_cycle(
                    motor.ADJUST_DUTY_MODE.ANGLE, target_angle=result["degree"], sec=4
                )
        mv.adjust_duty_cycle(motor.ADJUST_DUTY_MODE.ANGLE, target_angle=0, sec=15)


def main():
    init()
    goal_coordinate = {"lat": constants.GOAL_LAT, "lon": constants.GOAL_LON}
    current_coordinate = {"lat": None, "lon": None}
    try:
        threading.Thread(target=mv.move, daemon=True).start()
        # 初期位置取得
        while True:
            lat, lon, _, _, _ = gps.get_gps_data()
            if lat is not None and lon is not None:
                current_coordinate["lat"] = lat
                current_coordinate["lon"] = lon
                break
            time.sleep(1)
        mv.adjust_duty_cycle(mode=motor.ADJUST_DUTY_MODE.ANGLE, target_angle=0, sec=8)
        final_coordinate = gps_movement(goal_coordinate, current_coordinate, 5)
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
    finally:
        gps.disconnect()
        mv.running = False
        mv.cleanup()


if __name__ == "__main__":
    main()
