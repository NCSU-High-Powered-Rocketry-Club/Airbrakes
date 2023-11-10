# https://raspberrypi.stackexchange.com/questions/5100/detect-that-a-python-program-is-running-on-the-pi
def is_raspberrypi():
    import io

    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower(): return True
    except Exception: pass
    return False

# Set up mocking to allow us to test code even if we aren't running on a pi
# This feeds fake data to the flight software when we don't have
# IMU, servos, etc connected
if is_raspberrypi():
    # We are running on a pi
    from MSCLInterface import MSCLInterface
    from datetime import datetime
    now = datetime.now().strftime("%Y-%m-%d_%H:%M:%S") 
    interface = MSCLInterface("/dev/ttyACM0", open(f"./logs/{now}_rawLORDlog.csv", "w"),  open(f"./logs/{now}_estLORDlog.csv", "w"))

    from Servo import Servo

    # Numbers from trial and error
else:
    # We are not running on a pi, mock the IMU
    from MockServo import Servo
    from MockMSCLInterface import MockMSCLInterface
    interface = MockMSCLInterface()

# this is the pin that the servo's data wire is plugged into
SERVO_PIN = 32
servo = Servo(SERVO_PIN, 3.5, 11.5)