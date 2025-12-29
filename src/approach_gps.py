import logging
import logging.config
import threading
import time

import constants
import gpsnew
import motor


def init():
    logging.config.fileConfig("../config/logconfig.ini")
    gps = gpsnew.GPSModule()
    gps.connect()
    mv = motor.Motor()
    logging.info("Initialization completed successfully")
    return gps, mv


def gps_movement(target, current_coordinate, target_distance, gps, mv):
    while True:
        previous_coordinate = current_coordinate.copy()
        while True:
            lat, lon, satellites, utc_time, dop = gps.get_gps_data()
            if gpsnew.check_data(lat, lon, previous_coordinate):
                break
            else:
                logging.warning("The acquired location information is invalid. It is an abnormal value or NULL.")
                time.sleep(1)
        logging.info(f"{lat},{lon}\t{satellites}\t{dop}")
        current_coordinate = {"lat": lat, "lon": lon}
        result = gpsnew.calculate_target_distance_angle(
            current_coordinate, previous_coordinate, target, target_distance
        )
        match result["dir"]:
            case "Immediate":
                logging.info("GOAL!!!!!")
                return current_coordinate
            case None:
                logging.info(f"deg = {result['deg']}, dis = {result['distance']}")
                mv.adjust_duty_cycle(
                    motor.ADJUST_DUTY_MODE.ANGLE, target_angle=result["deg"], sec=8
                )
        logging.info(f"FORWARD")
        mv.adjust_duty_cycle(motor.ADJUST_DUTY_MODE.DIRECTION, direction="forward", sec=15)


def main():
    logging.info("Started")
    gps, mv = init()
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
            else:
                logging.warning("Location information cannot be obtained correctly.")
            time.sleep(1)
        mv.adjust_duty_cycle(mode=motor.ADJUST_DUTY_MODE.DIRECTION, direction="forward", sec=8)
        final_coordinate = gps_movement(goal_coordinate, current_coordinate, 5, gps, mv)
    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt")
    finally:
        logging.info("FINISH")
        gps.disconnect()
        mv.running = False
        mv.cleanup()


if __name__ == "__main__":
    main()
