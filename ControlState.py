import time

from ServoFactory import servo

from StateMachine import StateMachine
from ABDataPoint import ABDataPoint

class PID:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        
        self.last_error = 0
        self.integral = 0
        
    def process(self, error, dt):
        # TODO: Use existing PID implementation
        self.integral += error * dt
        derivative = (error - self.last_error) / dt
        
        self.last_error = error
        
        return self.kp * error + self.ki * self.integral + self.kd * derivative

class ControlState:
    """ Where we actually do the control loop """

    TARGET_APOGEE = 950

    last_dp: ABDataPoint = None
    
    velocity: float = 0
    
    def __init__(self, old_state):
        self.start_time = time.time()
        self.pid = PID(1, 0, 0) # TODO TUNE

    def process(self, state_machine: StateMachine, data_point: ABDataPoint):
        if (data_point.altitude is None):
            return

        if self.last_dp is None:
            self.last_dp = data_point
            return
        
        # timestamp is in ns, convert to seconds
        delta_time = (data_point.timestamp - self.last_dp.timestamp) / 1e9

        self.velocity = (data_point.altitude - self.last_dp.altitude) / delta_time

        # PID LOGIC
        predicted_apogee = self.predict_apogee()
        error = predicted_apogee - self.TARGET_APOGEE
        control = self.pid.process(error, data_point.timestamp - self.last_dp.timestamp)
        control = min(1, max(0, control)) * 1.0
        
        print(f"PID: {predicted_apogee:.5} {self.TARGET_APOGEE} {error} {data_point.altitude} {self.velocity} {control}")
        servo.set_command(control) # TODO
            
        self.last_dp = data_point

        # TODO: make a safer check for apogee
        if self.velocity < 0:
            quit()
            state_machine.to_state(FreefallState)

    def predict_apogee(self):
        # y = -0.5 * g * t^2 + v0 * t + y0

        a = -0.5 * 9.81
        b = self.velocity
        c = self.last_dp.altitude

        peak_time = -b / (2 * a)
        peak_altitude = a * peak_time ** 2 + b * peak_time + c
        
        return peak_altitude