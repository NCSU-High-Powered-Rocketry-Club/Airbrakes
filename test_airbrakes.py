from AirbrakeSystem.hardware.ServoInterface import Servo

# these angles represent open and closed for the airbrakes, they are arbitrary
SERVO_OFF_ANGLE =2 # 70
SERVO_ON_ANGLE =140.5 # 150

# this is the pin that the servo's data wire is plugged into
SERVO_PIN = 32

servo = Servo(SERVO_PIN, 3.5, 11.5)

print("Type (1) to deploy and (0) to retract the airbrakes.")
while True:
    command = input()
    if command == '0':
        servo.set_degrees(SERVO_OFF_ANGLE)
    elif command == '1':
        servo.set_degrees(SERVO_ON_ANGLE)
