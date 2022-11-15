import time
import os

LAUNCH_TO_TEST_TIME = 5
TEST_LENGTH_TIME = 5

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

class StandbyState:
    def __init__(self, old_state):
        set_servo(0)
        return

    def process(self, state_machine: StateMachine, data_point):
        accel = data_point['accel']
        if accel > 10:
            print("LIFTOFF")
            print(f"Acceleration is {accel}")
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
        set_servo(90)
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
        set_servo(0)
        return

    def process(self, state_machine: StateMachine, data_point):
        return

def main():
    interface.startLoggingLoopThread()

    print("started logging loop")

    state_machine = StateMachine(StandbyState)

    while True:
        try:
            data_point = interface.popDataPoint()
            if data_point is not None:
                state_machine.process_data_point(data_point)

        except KeyboardInterrupt:
            break

    interface.stopLoggingLoop()

if __name__ == "__main__":
    main()