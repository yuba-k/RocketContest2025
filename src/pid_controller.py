import time

class PID():
    def __init__(self,kp,ki,kd,setpoint,limits=(0,95),sample_time=0.05):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        self.limits = limits
        self.sample_time = sample_time

        self._last_time = None

    def calc(self,mesurment):
        if self._last_time is None:
            self._last_time = time.time()
            self._last_error = self.setpoint - mesurment
            return 0
        
        dt = time.time() - self._last_time

        if dt < self.sample_time:
            return None
        error = self.setpoint - mesurment
        self._integral += error * dt
        derivative = (error - self._last_error) / dt
        output = (self.kp * error) + (self.ki * self._integral) + (self.kd * derivative)

        low,high = self.limits
        output = max(low,output)
        output = min(high,output)

        self._last_time = time.time()
        self._last_error = error
        return output

