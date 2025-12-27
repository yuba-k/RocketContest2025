import logging
import logging.config
import threading
import time

import constants
import gpsnew
import motor

gps = None
mv = None


def init():
    global gps, mv
    logging.config.fileConfig("../config/logconfig.ini")
    gps = gpsnew.GPSModule()
    mv = motor.Motor()
    gps.connect()


def gps_movement(target, current_coordinate, target_distance):
    while True:
        previous_coordinate = current_coordinate.copy()
        while True:
            lat, lon, satellites, utc_time, dop = gps.get_gps_data()
            if gpsnew.check_data(lat, lon, previous_coordinate):
                break
            else:
                logging.warning("")
                time.sleep(1)
        current_coordinate = {"lat": lat, "lon": lon}
        result = gpsnew.calculate_target_distance_angle(
            current_coordinate, previous_coordinate, target, target_distance
        )
        match result["dir"]:
            case "Immediate":
                logging.info("GOAL!!!!!")
                return current_coordinate
            case None:
                logging.info(f"deg = {result['deg']}")
                mv.adjust_duty_cycle(
                    motor.ADJUST_DUTY_MODE.ANGLE, target_angle=result["deg"], sec=8
                )
            case "forward":
                pass
            case "left":
                logging.info(f"deg = {result['deg']}, left")
                mv.adjust_duty_cycle(
                    motor.ADJUST_DUTY_MODE.ANGLE, target_angle=result["deg"], sec=8
                )
            case "right":
                logging.info(f"deg = {result['deg']}, right")
                mv.adjust_duty_cycle(
                    motor.ADJUST_DUTY_MODE.ANGLE, target_angle=result["deg"], sec=8
                )
        logging.info(f"FORWARD")
        mv.adjust_duty_cycle(motor.ADJUST_DUTY_MODE.DIRECTION, direction="forward", sec=15)


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
        mv.adjust_duty_cycle(mode=motor.ADJUST_DUTY_MODE.DIRECTION, direction="forward", sec=8)
        final_coordinate = gps_movement(goal_coordinate, current_coordinate, 5)
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
    finally:
        logging.info("FINISH")
        gps.disconnect()
        mv.running = False
        mv.cleanup()


if __name__ == "__main__":
    main()
