from typing import Final

import configloading

confload = configloading.Config_reader()

INTERRUPTED_TIME: Final = 18 * 60

ST_PIN: Final = confload.reader("start", "st_pin", "intenger")

VOICE_SYNTH_ADDR: Final = confload.reader("i2c", "voice_synth_addr", "intenger16")
IMU_ADDR: Final = confload.reader("i2c", "imu_addr", "intenger16")

HEIGHT: Final = confload.reader("camera", "height", "intenger")
WIDTH: Final = confload.reader("camera", "width", "intenger")

DUTY: Final = confload.reader("motor", "duty", "intenger")
BASE_DUTY: Final = confload.reader("motor", "base_duty", "intenger")
RIGHT_PWM: Final = confload.reader("motor", "right_pwm", "intenger")
RIGHT_PHASE: Final = confload.reader("motor", "right_phase", "intenger")
LEFT_PWM: Final = confload.reader("motor", "left_pwm", "intenger")
LEFT_PHASE: Final = confload.reader("motor", "left_phase", "intenger")

KP: Final = confload.reader("pid", "kp", "float")
KI: Final = confload.reader("pid", "ki", "float")
KD: Final = confload.reader("pid", "kd", "float")

GOAL_LAT: Final = confload.reader("goal", "lat", "float")
GOAL_LON: Final = confload.reader("goal", "lon", "float")
RELAY_LAT: Final = GOAL_LAT + 0
RELAY_LAT: Final = GOAL_LON + 0