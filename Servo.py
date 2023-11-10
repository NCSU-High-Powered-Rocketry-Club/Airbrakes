import RPi.GPIO as GPIO

class Servo:
    command: float = 0.0
    
    def __init__(self, servoPin, minDuty, maxDuty):
        self.servoPin = servoPin
        GPIO.setwarnings(False)			#disable warnings
        GPIO.setmode(GPIO.BOARD)		#set pin numbering system

        # set the servo pin to output
        GPIO.setup(self.servoPin, GPIO.OUT)

        #create PWM instance with frequency
        self.pi_pwm = GPIO.PWM(self.servoPin, 50)

        # start PWM of required Duty Cycle
        self.pi_pwm.start(0) 

        # minimum duty cycle for left stop (determined with trial and error)
        self.servoMinDuty = minDuty #3.5
        # maximum duty cycle for right stop (determined with trial and error)
        self.servoMaxDuty = maxDuty #11.5

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
        print(f"Set servo angle {deg}")
        print(self.degrees_to_pos(deg))
        self.pi_pwm.ChangeDutyCycle(self.degrees_to_pos(deg))

    def set_command(self, command):
        print(f"Set servo command to {command:.3}")
        self.command = command
        self.set_degrees(command * 180) # TODO make work and clamp