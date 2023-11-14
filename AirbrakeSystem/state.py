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
        current_time = airbrakes.interface.last_time

        # print(f"time to go {MOTOR_BURN_TIME - (current_time - self.start_time)}")
        if current_time - self.start_time > (airbrakes.MOTOR_BURN_TIME * 1e9):
            # state_machine.to_state(TestState)
            airbrakes.to_state(ControlState)


class ControlState(AirbrakeState):
    """ Where we actually do the control loop """

    TARGET_APOGEE = 950

    def __init__(self, airbrakes: Airbrakes):
        self.start_time = time.time()
        self.pid = PID(1, 0, 0)  # TODO TUNE

        self.data_init = False
        self.velocity: float = 0

        super().__init__(airbrakes)

    def process(self, data_point: ABDataPoint):
        if (data_point.altitude is None):
            return

        if not self.data_init:
            self.last_dp = data_point
            self.data_init = True
            return

        # timestamp is in ns, convert to seconds
        delta_time = (data_point.timestamp - self.last_dp.timestamp) / 1e9
        if (delta_time == 0):
            delta_time = 0.01  # TODO: this shouldn't be needed once we have a real model

        self.velocity = (data_point.altitude -
                         self.last_dp.altitude) / delta_time

        # PID LOGIC
        predicted_apogee = self.predict_apogee()
        error = predicted_apogee - self.TARGET_APOGEE
        control = self.pid.process(
            error, data_point.timestamp - self.last_dp.timestamp)
        control = min(1, max(0, control)) * 1.0

        print(
            f"PID: {predicted_apogee:.5} {self.TARGET_APOGEE} {error} {data_point.altitude} {self.velocity} {control}")
        self.airbrakes.servo.set_command(control)  # TODO

        self.last_dp = data_point

        # TODO: make a safer check for apogee
        if self.velocity < 0:
            quit()
            # Airbrakes.to_state(FreefallState)

    def predict_apogee(self):
        # y = -0.5 * g * t^2 + v0 * t + y0

        a = -0.5 * 9.81
        b = self.velocity
        c = self.last_dp.altitude

        peak_time = -b / (2 * a)
        peak_altitude = a * peak_time ** 2 + b * peak_time + c

        return peak_altitude
