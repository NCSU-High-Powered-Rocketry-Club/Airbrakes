"""
Simulates the IMU interface for the rocket using OpenRocket
"""

import os
import sys
import threading
from queue import Queue

from AirbrakeSystem.data import ABDataPoint

import orhelper.orhelper as orhelper


OR_FILE_NAME = "Purple Nurple_Airbrakes.ork"
OR_FILE_PATH = os.path.join(os.path.dirname(__file__), OR_FILE_NAME)


class Airbrakes(orhelper.AbstractSimulationListener):
    """Max height the fins can go to"""

    MAX_HEIGHT = 0.03

    acceleration: float = 0.0

    fins: any

    def __init__(self, servo, queue) -> None:
        super().__init__()

        self.queue = queue
        self.servo = servo

    # pylint: disable-next=invalid-name
    def startSimulation(self, status):
        # Find the fin set
        for component in status.getConfiguration().getActiveComponents():
            if component.getName() == "Airbrakes":
                print("Found fin!")
                self.fins = component
                break

    # pylint: disable-next=invalid-name
    def postAccelerationCalculation(self, _status, acceleration_data):
        self.acceleration = acceleration_data.getLinearAccelerationWC().z

    # pylint: disable-next=invalid-name
    def postStep(self, status):

        timestamp = int(status.getSimulationTime() * 1e9)

        altitude = status.getRocketPosition().z
        velocity = status.getRocketVelocity().z

        data_point = ABDataPoint(self.acceleration, timestamp, altitude, velocity)
        # put in the queue
        # since the queue is size 1, this will block until the data point is popped
        self.queue.put(data_point)

        # Set the height of the fins
        new_height = self.MAX_HEIGHT * self.servo.get_command()
        self.fins.setHeight(new_height)


class MockMSCLInterface:
    last_time: int = 0
    airbrakes: Airbrakes = None

    def __init__(self, servo):
        """Mock constructor for MSCL interface"""

        self.servo = servo

        self.queue = Queue(1)

        self.instance = orhelper.OpenRocketInstance()
        self.instance.__enter__()

        self.or_thread = threading.Thread(target=self.start_or_thread)
        self.or_thread.start()

    def __del__(self):
        try:
            self.instance.__exit__(None, None, None)
        except RuntimeError:
            pass

    def start_or_thread(self):
        # TODO: this used a with block, might be memory leak but won't matter in practice
        orh = orhelper.Helper(self.instance)

        # Load document, run simulation and get data and events
        doc = orh.load_doc(OR_FILE_PATH)
        print(f"Number of simulations: {doc.getSimulationCount()}")
        sim = doc.getSimulation(doc.getSimulationCount() - 1)
        print(f"Simulation name: {sim.getName()}")

        self.airbrakes = Airbrakes(self.servo, self.queue)
        orh.run_simulation(sim, listeners=[self.airbrakes])

        self.queue.put("Done")

    def pop_data_point(self) -> ABDataPoint:
        dp: ABDataPoint = self.queue.get()
        try:
            self.last_time = dp.timestamp
        except AttributeError:
            pass

        # print(dp)
        return dp

    def start_logging_loop_thread(self):
        pass

    def stop_logging_loop(self):
        pass
