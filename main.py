import time
import os

LAUNCH_TO_TEST_TIME = 5
TEST_LENGTH_TIME = 5

SERVO_OFF_ANGLE = 0
SERVO_ON_ANGLE = 90

# https://raspberrypi.stackexchange.com/questions/5100/detect-that-a-python-program-is-running-on-the-pi
# TODO: Make sure this works on pi
def is_raspberrypi():
    import io

    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower(): return True
    except Exception: pass
    return False

# Set up mocking if we aren't running this on a pi
if is_raspberrypi():
    # We are running on a pi
    from MSCLInterface import MSCLInterface
    interface = MSCLInterface("/dev/ttyACM0", open("./logs/LORDlog.csv", "w"))

    from ServoController import set_servo
else:
    # We are not running on a pi, mock the IMU
    from MockMSCLInterface import MockMSCLInterface
    interface = MockMSCLInterface()

    # Mock the set_servo function
    def set_servo(deg):
        print(f"Setting servo to {deg}")

class StateMachine:
    def __init__(self, state):
        self.state = None
        self.to_state(state)

    def create_state(self, state):
        return state(self.state)

    def process_data_point(self, data_point):
        self.state.process(self, data_point)

    def to_state(self, new_state):
        print(f"Transitioning to state {new_state.__name__}")
        self.state = self.create_state(new_state)

LAUNCH_AVERAGE_SIZE = 10    
class StandbyState:
    def __init__(self, old_state):
        set_servo(SERVO_OFF_ANGLE)

        self.index = 0
        self.accelerations = [0] * LAUNCH_AVERAGE_SIZE
        return

    def process(self, state_machine: StateMachine, data_point):
        # Get the acceleration
        accel = data_point['accel']

        # Add it to the spot in the array, so that we can
        # calculate the rolling average
        self.accelerations[self.index] = accel
        # Move the index to the next spot, wrapping around
        self.index = (self.index + 1) % LAUNCH_AVERAGE_SIZE

        average_acceleration = sum(self.accelerations) / LAUNCH_AVERAGE_SIZE 
        if average_acceleration > 10:
            print("LIFTOFF")
            print(f"Acceleration is {average_acceleration}")
            state_machine.to_state(LiftoffState)

class LiftoffState:
    def __init__(self, old_state):
        self.start_time = time.time()

    def process(self, state_machine: StateMachine, data_point):
        current_time = time.time()

        if current_time - self.start_time > LAUNCH_TO_TEST_TIME:
            state_machine.to_state(TestState)
            return

        # print(f"time to go {LAUNCH_TO_TEST_TIME - (current_time - self.start_time)}")
        return

class TestState:
    def __init__(self, old_state):
        set_servo(SERVO_ON_ANGLE)
        self.start_time = time.time()
        return

    def process(self, state_machine: StateMachine, data_point):
        current_time = time.time()

        if current_time - self.start_time > TEST_LENGTH_TIME:
            state_machine.to_state(FreefallState)
            return
        return

class FreefallState:
    def __init__(self, old_state):
        set_servo(SERVO_OFF_ANGLE)
        return

    def process(self, state_machine: StateMachine, data_point):
        return

def main():
    interface.start_logging_loop_thread()

    print("started logging loop")

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