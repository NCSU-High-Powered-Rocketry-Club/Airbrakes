# main.py is a state machine that controls the flight of the rocket
# The flight consists of 4 sections
# 1. Standby: While the rocket is on the ground, detects launch
# 2. Liftoff: Starts when the rocket takes off, starts a timer to begin testing
# 3. Test: Does the testing of the airbrakes
# 4. Freefall: After the test, resets the rocket

import time

from StateMachine import StateMachine

LAUNCH_TO_TEST_TIME = 5 # Time from liftoff detected to test start
TEST_LENGTH_TIME = 4 # Length of the test

# TODO: Configure these to the appropriate values
SERVO_OFF_ANGLE = 120
SERVO_ON_ANGLE = 45

# TODO: Make sure this is the right pin
SERVO_PIN = 32

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
    interface = MSCLInterface("/dev/ttyACM0", open("./logs/LORDlog.csv", "w"))

    from Servo import Servo
else:
    # We are not running on a pi, mock the IMU
    from MockMSCLInterface import MockMSCLInterface
    interface = MockMSCLInterface()

    # Mock the servo
    from MockServo import Servo

class StandbyState:
    AVERAGE_COUNT = 250
    # require an acceleration of 5m/s^2
    ACCELERATION_REQUIREMENT = 5

    def __init__(self, old_state):
        set_degrees(SERVO_OFF_ANGLE)

        # We create an array to store the last n accelerations
        # in order to find the moving average.
        # We store an index to replace a different value in the array
        # every time, looping back at the end
        self.index = 0
        self.accelerations = [0] * StandbyState.AVERAGE_COUNT
        return

    def process(self, state_machine: StateMachine, data_point):
        # Get the acceleration
        accel = data_point['accel']

        # Add it to the spot in the array, so that we can
        # calculate the rolling average
        self.accelerations[self.index] = accel
        # Move the index to the next spot, wrapping around
        self.index = (self.index + 1) % StandbyState.AVERAGE_COUNT

        # print(self.accelerations)

        average_acceleration = sum(self.accelerations) / StandbyState.AVERAGE_COUNT 
        
        # We have to use the absolute value of acceleration here because
        # the actual acceleration will be a large negative number.
        # If you were standing on the IMU, you would feel heavier when
        # liftoff happens, so acceleration goes from -9.8 -> -15 (or some number).
        # Really, it should be `average_acceleration <= StandbyState.ACCELERATION_REQUIREMENT`
        # where the requirement is also negative, but this way works for both cases
        if abs(average_acceleration) >= StandbyState.ACCELERATION_REQUIREMENT:
            print("LIFTOFF")
            print(f"Acceleration is {average_acceleration}")
            print(f"Average acceleration is {self.accelerations}")
            state_machine.to_state(LiftoffState)

class LiftoffState:
    def __init__(self, old_state):
        self.start_time = time.time()

    def process(self, state_machine: StateMachine, data_point):
        current_time = time.time()

        # print(f"time to go {LAUNCH_TO_TEST_TIME - (current_time - self.start_time)}")
        if current_time - self.start_time > LAUNCH_TO_TEST_TIME:
            state_machine.to_state(TestState)

class TestState:
    def __init__(self, old_state):
        set_degrees(SERVO_ON_ANGLE)
        self.start_time = time.time()

    def process(self, state_machine: StateMachine, data_point):
        current_time = time.time()

        if current_time - self.start_time > TEST_LENGTH_TIME:
            state_machine.to_state(FreefallState)

class FreefallState:
    def __init__(self, old_state):
        set_degrees(SERVO_OFF_ANGLE)

    def process(self, state_machine: StateMachine, data_point):
        return

# TODO (After launch): There's a better way to do this, but this has been tested and works
servo: Servo
def set_degrees(deg):
    global servo
    servo.set_degrees(deg)

def main():
    interface.start_logging_loop_thread()

    print("started logging loop")

    global servo
    # Numbers from trial and error
    servo = Servo(SERVO_PIN, 3.5, 11.5)

    #servo.set_degrees(45)

    state_machine = StateMachine(StandbyState)

    while True:
        try:
            data_point = interface.pop_data_point()
            if data_point is not None:
                state_machine.process_data_point(data_point)

        except KeyboardInterrupt:
            break

    interface.stop_logging_loop()

if __name__ == "__main__":
    main()
