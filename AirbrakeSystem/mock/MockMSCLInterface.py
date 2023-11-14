import numpy as np
from ..data import ABDataPoint

'''
Module / Class created for simulating the flight of a rocket using 1D motion approximations.
All unites in SI / metric unless explicitly stated otherwise
'''


class RocketModel1D:
    itmax = 10000  # maximum number of simulation iterations

    def __init__(self, mass, area, drag_coeff, servo, density_model=1, gravtiy_model=1):
        # Define the rocket
        self.mass = mass
        self.massi = 1/mass
        self.ref_area = area  # reference area for the drag coefficient
        self.Cd = drag_coeff
        self.density_model = density_model
        self.gravity_model = gravtiy_model
        # state = np.array([position, velocity])
        self.state = np.array([0.0, 0.0])
        self.time = 0

        self.servo = servo

    def initialize(self, position, velocity):
        self.state[0] = position
        self.state[1] = velocity
        self.time = 0

    def set_timestep(self, dt):
        self.dt = dt

    def CdA(self):
        return (self.Cd * (1 + self.servo.command * 0.5)) * self.ref_area

    def rho(self):
        if (self.density_model == 1):
            return 1.2
        else:
            return float('NaN')

    def g(self):
        if (self.gravity_model == 1):
            return 9.81
        else:
            return float('NaN')

    def drag_force(self, velocity):
        vmag = abs(velocity)
        return 0.5*self.rho()*vmag*velocity*self.CdA()

    def thrust_force(self):
        return 1520 if self.time < 2.1 else 0

    def acceleration(self):
        return (self.thrust_force()-self.drag_force(self.state[1]))*self.massi - self.g()

    def euler_step(self):
        self.state += self.dt * np.array([self.state[1], self.acceleration()])
        self.time += self.dt

    def sim_to_apogee(self):
        iter = 0
        self.heights = []
        self.times = []

        self.heights.append(self.state[0])
        self.times.append(0)

        while (self.state[1] > 0) and (iter < self.itmax):
            self.euler_step()

            self.heights.append(self.state[0])
            self.times.append(self.time)
            iter += 1

        return self.state[0]


# TODO: TUNE
rkt_mass = 19  # kg
rkt_area = 0.018  # m Cross sectional area
Cd = 0.6  # drag coefficient ~1.0 if airbrakes

HOLD_TIME = 100  # Time from start of sim to liftoff

# test_rock = rocket_model_1D(rkt_mass, rxt_area, Cd)


class MSCLInterface:
    """
    Mocks the IMU with a 1D model
    """
    model: RocketModel1D
    last_time: int = 0

    def __init__(self, port, raw_data_logfile, est_data_logfile, servo):
        """Mock constructor for MSCL interface

        Args:
            port (any): Unused parameter, kept for consistency
            raw_data_logfile (any): Unused, kept for consistency
            est_data_logfile (any): Unused, kept for consistency
        """

        self.model = RocketModel1D(rkt_mass, rkt_area, Cd, servo)
        self.model.set_timestep(0.001)
        self.model.initialize(0, 0)
        self.iter = 0

    def start_logging_loop_thread(self):
        return

    def pop_data_point(self) -> ABDataPoint:
        self.iter += 1
        import time
        # time.sleep(0.001)

        res = ABDataPoint(0.0, 0, 0.0)

        if (self.iter < HOLD_TIME):
            res.timestamp = 0
            res.accel = 0.0
            res.altitude = 0.0
        else:
            self.model.euler_step()

            res.timestamp = int(self.model.time * 1e9)
            res.accel = self.model.acceleration()
            res.altitude = self.model.state[0]

        print(f"{(res.timestamp / 1e9) : 8.3} {res.accel:8.3} {res.altitude:.4}")
        self.last_time = res.timestamp
        return res

    def stop_logging_loop(self):
        return
