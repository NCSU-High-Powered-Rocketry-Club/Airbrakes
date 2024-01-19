import threading
from ..data import ABDataPoint

import os
import sys
from queue import Queue

# Add orhelper to path
script_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_path, '../../orhelper'))

import orhelper

class Airbrakes(orhelper.AbstractSimulationListener):
    """ Max height the fins can go to """
    max_height = 0.03

    def __init__(self, servo, queue) -> None:
        super().__init__()

        self.queue = queue
        self.servo = servo
    
    def startSimulation(self, status):
        # Find the fin set
        for component in status.getConfiguration().getActiveComponents():
            if component.getName() == "Airbrakes":
                print("Found fin!")
                self.fins = component
                break

    def postStep(self, status):
        # TODO: This is 0 until apogee. Why?
        accel_vec = status.getRocketAcceleration()
        accel = accel_vec.z
        
        timestamp = status.getSimulationTime() * 1e9

        altitude = status.getRocketPosition().z
        
        data_point = ABDataPoint(accel, timestamp, altitude)
        self.queue.put(data_point)
        
        # -----
        new_height = self.max_height * self.servo.get_command()
        self.fins.setHeight(new_height)

class MSCLInterface:
    last_time: int = 0
    airbrakes: Airbrakes = None

    def __init__(self, servo):
        """Mock constructor for MSCL interface"""

        self.servo = servo

        self.queue = Queue(1)

        self.or_thread = threading.Thread(target=self.start_or_thread)
        self.or_thread.start()

    def start_or_thread(self):
        # TODO: this used a with block, might be memory leak but won't matter in practice
        with orhelper.OpenRocketInstance() as instance:
            orh = orhelper.Helper(instance)

            # Load document, run simulation and get data and events
            doc = orh.load_doc(os.path.join(script_path, 'Purple Nurple_Airbrakes.ork'))
            print(f"Number of simulations: {doc.getSimulationCount()}")
            sim = doc.getSimulation(doc.getSimulationCount() - 1)
            print(f"Simulation name: {sim.getName()}")

            self.airbrakes = Airbrakes(self.servo, self.queue)
            orh.run_simulation(sim, listeners=[self.airbrakes])

    def start_logging_loop_thread(self):
        return

    def pop_data_point(self) -> ABDataPoint:
        dp = self.queue.get()

        print(f"Got data point: {dp}")
        return dp

    def stop_logging_loop(self):
        return
