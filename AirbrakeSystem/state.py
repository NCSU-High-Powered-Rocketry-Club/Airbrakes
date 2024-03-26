from __future__ import annotations
import logging
from typing import TYPE_CHECKING
from AirbrakeSystem.lookup_table_control import *
import time

if TYPE_CHECKING:
    from .airbrakes import Airbrakes

from .data import ABDataPoint
from .control import PID

logger = logging.getLogger("airbrakes_data")


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
    """Where we actually do the control loop"""

    alt_readings = [0.0] * 50
    idx = 0
    max_altitude = 0
    change_in_altitude_lookup_table = load_sorted_pid_lookup_table()
    bang_bang_lookup_table = load_bang_bang_lookup_table()
    target_apogee = 700.0
    last_altitude = 0

    # We want to make sure the airbrakes are deployed for at least 0.5 seconds
    hard_coded_deploy_length = 0.5

    def __init__(self, airbrakes: Airbrakes):
        self.airbrakes = airbrakes
        self.deploy_time: float = airbrakes.interface.last_time / 1000000000.0
        print(f"deploy time: {self.deploy_time}")
        airbrakes.servo.set_degrees(airbrakes.SERVO_ON_ANGLE)
        super().__init__(airbrakes)

    def process(self, data_point: ABDataPoint):
        current_velocity = self.airbrakes.velocity
        current_extension = self.airbrakes.servo.get_command()
        estimated_apogee = self.airbrakes.altitude + estimate_change_in_altitude(self.change_in_altitude_lookup_table,
                                                                                 current_velocity, current_extension)

        logger.info("Predicted Apogee,%.3f", estimated_apogee)
        logger.info("Servo Control,%.3f", current_extension)

        estimated_change_in_altitude = get_bang_bang_change_in_altitude(self.bang_bang_lookup_table, current_velocity)

        if estimated_change_in_altitude is not None:
            if get_bang_bang_change_in_altitude(self.bang_bang_lookup_table, current_velocity) + self.airbrakes.altitude <= self.target_apogee:
                self.airbrakes.servo.set_command(0.0)
            else:
                self.airbrakes.servo.set_command(1.0)

        # Deploys the airbrakes regardless for the first .5s
        if self.airbrakes.interface.last_time / 1000000000.0 - self.deploy_time <= self.hard_coded_deploy_length:
            self.airbrakes.servo.set_command(1.0)

        # If the altitude is new
        if self.last_altitude != data_point.altitude:
            self.last_altitude = data_point.altitude
            if data_point.altitude >= self.max_altitude:
                self.max_altitude = data_point.altitude

        # Checks if we are more than 30 meters below apogee
        if data_point.altitude <= self.max_altitude - 30:
            print(f"apogee: {data_point.altitude} m")
            self.airbrakes.to_state(FreefallState)


class FreefallState(AirbrakeState):
    def __init__(self, airbrakes: Airbrakes):
        print(f"retract time: {airbrakes.interface.last_time / 1e9}")
        airbrakes.servo.set_degrees(airbrakes.SERVO_OFF_ANGLE)

    def process(self, data_point: ABDataPoint):
        pass
