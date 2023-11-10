# main.py is a state machine that controls the flight of the rocket
# The flight consists of 4 sections
# 1. Standby: While the rocket is on the ground, detects launch
# 2. Liftoff: Starts when the rocket takes off, starts a timer to begin testing
# 3. Test: Does the testing of the airbrakes
# 4. Freefall: After the test, resets the rocket

import time

from imports import interface, servo

from StateMachine import StateMachine
from ControlState import ControlState

from ABDataPoint import ABDataPoint

MOTOR_BURN_TIME = 2 # Time from liftoff detected to control start
TEST_LENGTH_TIME = 4 # Length of the test

# these angles represent open and closed for the airbrakes, they are arbitrary
SERVO_OFF_ANGLE = 84.5
SERVO_ON_ANGLE = 164.5

class StandbyState:
    """
    On the launch pad
    """
    AVERAGE_COUNT = 250
    # require an acceleration of 5m/s^2
    ACCELERATION_REQUIREMENT = 5

    def __init__(self, old_state):
        servo.set_degrees(SERVO_OFF_ANGLE)

        # We create an array to store the last n accelerations
        # in order to find the moving average.
        # We store an index to replace a different value in the array
        # every time, looping back at the end
        self.index = 0
        self.accelerations = [0] * StandbyState.AVERAGE_COUNT
        return


    def process(self, state_machine: StateMachine, data_point: ABDataPoint):
        # Get the acceleration
        accel = data_point.accel

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
    """
    During motor burn
    """
    def __init__(self, old_state):
        self.start_time = time.time()

    def process(self, state_machine: StateMachine, data_point: ABDataPoint):
        current_time = time.time()

        # print(f"time to go {MOTOR_BURN_TIME - (current_time - self.start_time)}")
        if current_time - self.start_time > MOTOR_BURN_TIME:
            state_machine.to_state(TestState)
            state_machine.to_state(ControlState)


class TestState:
    """
    Test deploy airbrakes for a few seconds
    """
    def __init__(self, old_state):
        servo.set_degrees(SERVO_ON_ANGLE)
        self.start_time = time.time()

    def process(self, state_machine: StateMachine, data_point: ABDataPoint):
        current_time = time.time()

        if current_time - self.start_time > TEST_LENGTH_TIME:
            state_machine.to_state(FreefallState)


def main():
    interface.start_logging_loop_thread()

    print("started logging loop")

    #servo.set_degrees(SERVO_OFF_ANGLE)

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
