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
