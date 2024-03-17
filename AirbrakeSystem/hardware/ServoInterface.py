import RPi.GPIO as GPIO


class Servo:
    command: float = 0.0

    def __init__(self, servo_pin, closed_duty, open_duty):
        self.servo_pin = servo_pin
        GPIO.setwarnings(False)  # disable warnings
        GPIO.setmode(GPIO.BOARD)  # set pin numbering system

        # set the servo pin to output
        GPIO.setup(self.servo_pin, GPIO.OUT)

        # create PWM instance with frequency
        self.pi_pwm = GPIO.PWM(self.servo_pin, 50)

        # start PWM of required Duty Cycle
        self.pi_pwm.start(0)

        # minimum duty cycle for left stop (determined with trial and error)
        self.servo_closed_duty = closed_duty  # 3.5
        # maximum duty cycle for right stop (determined with trial and error)
        self.servo_open_duty = open_duty  # 11.5

    def set_command(self, command):
        command = float(command)
        if command > 1:
            command = 1.0
        if command < 0:
            command = 0.0

        logger.info("Servo Control,%.3f", command)
        self.command = command
        self.pi_pwm.ChangeDutyCycle(
            (self.servo_closed_duty)(1.0 - command) + (self.servo_open_duty * command)
        )

    def get_command(self):
        return self.command
