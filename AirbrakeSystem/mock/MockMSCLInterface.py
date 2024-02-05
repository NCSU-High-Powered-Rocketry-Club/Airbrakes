"""
Simulates the IMU interface for the rocket using OpenRocket
"""

import os
import sys
import csv
import threading
from queue import Queue

from ..data import ABDataPoint

# Add orhelper to path
script_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_path, '../../orhelper'))

import orhelper


class Airbrakes(orhelper.AbstractSimulationListener):
    """ Max height the fins can go to """
    max_height = 0.03

    acceleration: float = 0.0

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
    def postAccelerationCalculation(self, status, acceleration_data):
        self.acceleration = acceleration_data.getLinearAccelerationWC().z
    
    # pylint: disable-next=invalid-name
    def postStep(self, status):
        
        timestamp = int(status.getSimulationTime() * 1e9)

        altitude = status.getRocketPosition().z
        
        data_point = ABDataPoint(self.acceleration, timestamp, altitude)
        # put in the queue
        # since the queue is size 1, this will block until the data point is popped
        self.queue.put(data_point)
        
        # Set the height of the fins
        new_height = self.max_height * self.servo.get_command()
        self.fins.setHeight(new_height)


class MockMSCLInterface:
    last_time: int = 0
    airbrakes: Airbrakes = None
    list_of_data_points: list[dict] = []

    def __init__(self, servo):
        """Mock constructor for MSCL interface"""

        self.servo = servo

        self.queue = Queue(1)

        self.instance = orhelper.OpenRocketInstance()
        self.instance.__enter__()

        self.or_thread = threading.Thread(target=self.start_or_thread)
        self.or_thread.start()

    def __del__(self):
        self.instance.__exit__(None, None, None)

    def start_or_thread(self):
        # TODO: this used a with block, might be memory leak but won't matter in practice
        orh = orhelper.Helper(self.instance)

        # Load document, run simulation and get data and events
        doc = orh.load_doc(os.path.join(script_path, 'Purple Nurple_Airbrakes.ork'))
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
            # I'm going to hijack this method for data logging
            self.list_of_data_points.append({
                "timestamp": dp.timestamp,
                "altitude": dp.altitude,
                "accel": dp.accel
            })
        except AttributeError:
            pass

        # print(dp)
        return dp

    # Because this is all simulated, we don't really need to log as it's going,
    # just store all the points in a list, then log it at the end
    def start_logging_loop_thread(self):
        pass

    # In the simulation, we can just log everything at the end
    def stop_logging_loop(self):
        # TODO I'm not sure what format we want logging to be in, so this should be fixed as needed
        filename = "simulation.csv"
        headers = ["timestamp", "altitude", "accel"]
        # writing to csv file
        with open(filename, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(self.list_of_data_points)
