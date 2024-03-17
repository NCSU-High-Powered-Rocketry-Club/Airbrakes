import os

import numpy as np
import orhelper.orhelper as orhelper
from orhelper.orhelper import FlightDataType, FlightEvent


from AirbrakeSystem.mock.MockMSCLInterface import Airbrakes


class StaticAirbrakes(orhelper.AbstractSimulationListener):

    amount: float

    def __init__(self, amount) -> None:
        super().__init__()
        self.amount = amount

    # pylint: disable-next=invalid-name
    def startSimulation(self, status):
        # Find the fin set
        for component in status.getConfiguration().getActiveComponents():
            if component.getName() == "Airbrakes":
                print(f"Setting airbrake to {self.amount}")
                component.setHeight(self.amount * Airbrakes.MAX_HEIGHT)
                break


OR_FILE_NAME = "Purple Nurple_Airbrakes.ork"
OR_FILE_PATH = os.path.join(
    os.path.dirname(__file__), "../AirbrakeSystem/mock/", OR_FILE_NAME
)

print(f"Loading {OR_FILE_PATH}")


def run_simulation(airbrakes):
    orh.run_simulation(sim, listeners=[airbrakes])

    data = orh.get_timeseries(
        sim,
        [
            FlightDataType.TYPE_TIME,
            FlightDataType.TYPE_ALTITUDE,
            FlightDataType.TYPE_VELOCITY_Z,
        ],
    )
    events = orh.get_events(sim)

    index_at = lambda t: (np.abs(data[FlightDataType.TYPE_TIME] - t)).argmin()

    burnout_time = 0
    apogee = 0
    apogee_time = 0
    for event, time in events.items():
        if event == FlightEvent.BURNOUT:
            burnout_time = time[0]
            print(f"Burnout time: {burnout_time}")
        if event == FlightEvent.APOGEE:
            apogee_time = time
            apogee = data[FlightDataType.TYPE_ALTITUDE][index_at(apogee_time)]

            print(f"Apogee time: {apogee}")

    # Make a list of (time, velocity, altitude) tuples from burnout to apogee_time
    # Map the altitude to apogee-altitude
    # get rid of the time
    # write to a csv
    data = map(
        lambda x: (x[1], apogee - x[2]),
        filter(
            lambda x: x[0] > burnout_time and x[0] < apogee_time,
            zip(
                data[FlightDataType.TYPE_TIME],
                data[FlightDataType.TYPE_VELOCITY_Z],
                data[FlightDataType.TYPE_ALTITUDE],
            ),
        ),
    )

    return data


def round_and_average(tuples):
    rounded_values = {}

    # Round x-values to integers and store corresponding y-values
    for x, y in tuples:
        rounded_x = round(x)
        if rounded_x in rounded_values:
            rounded_values[rounded_x].append(y)
        else:
            rounded_values[rounded_x] = [y]

    # Calculate average y-values for each unique rounded x-value
    result = [
        (int(rounded_x), sum(y_values) / len(y_values))
        for rounded_x, y_values in rounded_values.items()
    ]

    return result


values = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
datas = []
with orhelper.OpenRocketInstance() as instance:
    orh = orhelper.Helper(instance)

    doc = orh.load_doc(OR_FILE_PATH)
    print(f"Number of simulations: {doc.getSimulationCount()}")
    sim = doc.getSimulation(doc.getSimulationCount() - 1)
    print(f"Simulation name: {sim.getName()}")

    # lists of (velocity, delta_h) tuples
    datas = [round_and_average(run_simulation(StaticAirbrakes(v))) for v in values]

import pandas

df = pandas.DataFrame(datas[0], columns=["velocity", "airbrakes_0.0"])
for i in range(1, len(datas)):
    df = df.merge(
        pandas.DataFrame(datas[i], columns=["velocity", f"airbrakes_{values[i]}"]),
        on="velocity",
        how="outer",
    )

print(df)
df.to_csv("lookup_table.csv", index=False)

import plotly.express as px

fig = px.line(
    df,
    x="velocity",
    y=df.columns[1:],
    labels={
        "value": "Delta h (m)",
        "velocity": "Velocity (m/s)",
    },
    title="Delta h vs velocity for various airbrakes",
)
fig.layout.template = "plotly_dark"
fig.show()
