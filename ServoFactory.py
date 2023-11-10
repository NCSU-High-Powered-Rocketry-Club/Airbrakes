import sys

if "MockServo" in sys.argv or "MockAll" in sys.argv:
    from MockServo import Servo
else:
    from Servo import Servo

print("ServoFactory.py")

# this is the pin that the servo's data wire is plugged into
SERVO_PIN = 32
servo = Servo(SERVO_PIN, 3.5, 11.5)