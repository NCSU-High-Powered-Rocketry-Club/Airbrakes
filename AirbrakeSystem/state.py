from __future__ import annotations
from typing import TYPE_CHECKING
import time

if TYPE_CHECKING:
    from .airbrakes import Airbrakes

from .data import ABDataPoint
from .control import PID

# The flight consists of 4 sections
# 1. Standby: While the rocket is on the ground, detects launch
# 2. Liftoff: Starts when the rocket takes off, starts a timer to begin testing
# 3. Test: Does the testing of the airbrakes
# 4. Freefall: After the test, resets the rocket


class AirbrakeState:
    def __init__(self, airbrakes: Airbrakes):
        self.airbrakes = airbrakes


class StandbyState(AirbrakeState):
    """
    On the launch pad
    """
    AVERAGE_COUNT = 250
    # require an acceleration of 5m/s^2
    ACCELERATION_REQUIREMENT = 5

    def __init__(self, airbrakes: Airbrakes):

        airbrakes.servo.set_degrees(airbrakes.SERVO_OFF_ANGLE)

        # We create an array to store the last n accelerations
        # in order to find the moving average.
        # We store an index to replace a different value in the array
        # every time, looping back at the end
        self.index = 0
        self.accelerations = [0.0] * StandbyState.AVERAGE_COUNT

        super().__init__(airbrakes)

    def process(self, data_point: ABDataPoint):
        # Get the acceleration
        accel = data_point.accel

        # Add it to the spot in the array, so that we can
        # calculate the rolling average
        self.accelerations[self.index] = accel
        # Move the index to the next spot, wrapping around
        self.index = (self.index + 1) % StandbyState.AVERAGE_COUNT

        # print(self.accelerations)

        average_acceleration = sum(
            self.accelerations) / StandbyState.AVERAGE_COUNT

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
            self.airbrakes.to_state(LiftoffState)


class LiftoffState(AirbrakeState):
    """
    During motor burn
    """

    def __init__(self, airbrakes: Airbrakes):
        self.start_time = airbrakes.interface.last_time
        super().__init__(airbrakes)

    def process(self, data_point: ABDataPoint):
        airbrakes = self.airbrakes
        current_time = data_point.timestamp

        # print(f"time to go {MOTOR_BURN_TIME - (current_time - self.start_time)}")
        if current_time - self.start_time > (airbrakes.MOTOR_BURN_TIME * 1e9):
            # state_machine.to_state(TestState)
            airbrakes.to_state(ControlState)

class ControlState(AirbrakeState):
    """ Where we actually do the control loop """

    apogee_check_c = 0
    alt_readings = [0.0] * 250
    idx = 0 
    max_alt_avg = 0

    pid: PID = PID(0.01, 0.0, 0.0)

    def __init__(self, airbrakes: Airbrakes):
        print(f"deploy time: {airbrakes.interface.last_time / 1e9}")
        airbrakes.servo.set_degrees(airbrakes.SERVO_ON_ANGLE)
        super().__init__(airbrakes)

    def process(self, data_point: ABDataPoint):
        
        # TODO: predict apogee

        # TODO: Control the servo based on apogee

        # detect apogee and switch to freefall state
        self.alt_readings[self.idx] = data_point.altitude
        self.idx = (self.idx+1) % 250

        alt_avg = int(sum(self.alt_readings)/250)

        if (alt_avg > self.max_alt_avg):
            self.max_alt_avg = alt_avg
            self.apogee_check_c = 0
        else:
            self.apogee_check_c += 1

        if (self.apogee_check_c == 1000):
            print(f"apogee: {self.max_alt_avg} m")
            self.airbrakes.to_state(FreefallState)

class FreefallState(AirbrakeState):
    def __init__(self, airbrakes: Airbrakes):
        print(f"retract time: {airbrakes.interface.last_time / 1e9}")
        airbrakes.servo.set_degrees(airbrakes.SERVO_OFF_ANGLE)

    def process(self, data_point: ABDataPoint):
        pass
