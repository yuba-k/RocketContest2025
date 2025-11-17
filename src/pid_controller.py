import time

class PID():
    def __init__(self,kp,ki,kd,setpoint,limits=(-15,15),sample_time=0.05):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        self.limits = limits
        self.sample_time = sample_time

        self._last_time = None
        self._last_error = 0
        self._integral = 0
        self._last_output = 0

    def calc(self,measurement):
        if self._last_time is None:
            self._last_time = time.perf_counter()
            self._last_error = self.setpoint - measurement
            return 0
        
        currenttime = time.perf_counter()

        dt = currenttime - self._last_time

        if dt < self.sample_time:
            return self._last_output
        error = self.setpoint - measurement
        self._integral += error * dt
        derivative = (error - self._last_error) / dt
        output = (self.kp * error) + (self.ki * self._integral) + (self.kd * derivative)

        low,high = self.limits
        output = max(low,output)
        output = min(high,output)

        self._last_time = currenttime
        self._last_error = error
        self._last_output = output
        return output

    def reset(self,setpoint):
        self._last_time = None
        self._last_error = 0
        self._integral = 0
        self._last_output = 0
        self.setpoint = setpoint