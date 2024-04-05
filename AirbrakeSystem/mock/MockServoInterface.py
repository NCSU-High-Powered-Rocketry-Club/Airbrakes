import logging

logger = logging.getLogger("airbrakes_data")


class Servo:
    _command: float = 0.0  # 0 to 1

    def __init__(self, servo_pin, min_duty, max_duty):
        self.servo_pin = servo_pin
        # minimum duty cycle for left stop (determined with trial and error)
        self.servo_min_duty = min_duty  # 3.5
        # maximum duty cycle for right stop (determined with trial and error)
        self.servo_max_duty = max_duty  # 11.5
        print(
            f"Set up servo with pin: {servo_pin}, minDuty: {min_duty}, maxDuty: {max_duty}"
        )

    def set_command(self, command):
        command = float(command)
        if command > 1:
            command = 1.0
        if command < 0:
            command = 0.0

        logger.info("Servo Control,%.3f", command)
        self._command = command

    def get_command(self):
        return self._command
