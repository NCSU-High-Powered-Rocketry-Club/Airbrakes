class Servo:
    command: float = 0.0 # 0 to 1
    
    def __init__(self, servoPin, minDuty, maxDuty):
        self.servoPin = servoPin
        # minimum duty cycle for left stop (determined with trial and error)
        self.servoMinDuty = minDuty #3.5
        # maximum duty cycle for right stop (determined with trial and error)
        self.servoMaxDuty = maxDuty #11.5
        print(f"Set up servo with pin: {servoPin}, minDuty: {minDuty}, maxDuty: {maxDuty}")

    # this function converts the degree value to rotate the 
    def degrees_to_pos(self,deg):
        # if (deg > 180) or (deg < 0):
            # raise ValueError("Value not between 0 and 180")

        # Clamp the value to between 0 and 180
        if (deg > 180):
            deg = 180
        if (deg < 0):
            deg = 0

        return ((deg * (self.servoMaxDuty - self.servoMinDuty)) / 180) + self.servoMinDuty

    def set_degrees(self, deg):
        print(f"Set servo angle to {deg:.3}")
        # pass

    def set_command(self, command):
        if command > 1:
            command = 1.0
        if command < 0:
            command = 0.0

        print(f"Set servo command to {command:.3}")
        self.command = command
        # self.set_degrees(command * 180) # TODO make good
