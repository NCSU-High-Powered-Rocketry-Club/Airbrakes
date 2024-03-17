import sys
import pandas as pd
import plotly.graph_objects as go

# Run this file after you have run the simulation (python .\main.py -si)

# Read the log file
if len(sys.argv) < 2:
    # Get the newest file from the logs folder
    import os

    logs = os.listdir("./logs")
    logs.sort()
    filename = "./logs/" + logs[-1]
else:
    filename = sys.argv[1]

print(f"Reading log file: {filename}")

with open(filename, "r") as file:
    lines = file.readlines()

# Initialize lists to store data
data = {
    "timestamp": [],
    "altitude": [],
    "acceleration": [],
    "predicted_apogee": [],
    "servo_control": [],
    "average_altitude": [],
}

state_changes = []


def format_name(name):
    return name.lower().replace(" ", "_")


# Process each line in the log file
for line in lines:
    if line.isspace():
        continue

    parts = line.strip().split(",")
    timestamp = int(parts[0])
    data["timestamp"].append(timestamp)

    event_type = parts[1]
    if event_type == "Data point":
        data["altitude"].append(float(parts[2]))
        data["acceleration"].append(float(parts[3]))
    elif event_type == "State Change":
        data["timestamp"].pop()
        # remove the 'State' suffix
        name = parts[2][:-5]
        state_changes.append((timestamp, name))
    else:
        try:
            data[format_name(event_type)].append(float(parts[2]))
        except:
            # make sure the lists are aligned
            print("Unexpected event type: ", event_type)
            data["timestamp"].pop()

    for key in data:
        if len(data[key]) < len(data["timestamp"]):
            data[key].append(None)

# Create a pandas dataframe
df = pd.DataFrame(data)

# Merge rows with the same timestamp
df = df.groupby("timestamp").agg(
    lambda x: x.dropna().iloc[0] if x.notnull().any() else None
)

print(df)

# Create traces for Altitude and Acceleration
trace_altitude = go.Scatter(
    x=df.index, y=df["altitude"], mode="lines", name="Altitude", line=dict(color="blue")
)
trace_accel = go.Scatter(
    x=df.index,
    y=df["acceleration"],
    mode="lines",
    name="Acceleration",
    line=dict(color="red"),
)
trace_predicted_apogee = go.Scatter(
    x=df.index,
    y=df["predicted_apogee"],
    mode="lines",
    name="Predicted Apogee",
    line=dict(color="green"),
)
trace_servo_control = go.Scatter(
    x=df.index,
    y=df["servo_control"],
    mode="lines",
    name="Servo Control",
    line=dict(color="purple"),
)
trace_average_altitude = go.Scatter(
    x=df.index,
    y=df["average_altitude"],
    mode="lines",
    name="Average Altitude",
    line=dict(color="orange"),
)
trace_average_altitude.visible = "legendonly"

# Create layout
layout = go.Layout(
    title="Simulation Data Over Time",
    xaxis=dict(title="Time"),
    yaxis=dict(title="Simulation Data"),
)

# Create figure
fig = go.Figure(
    data=[
        trace_altitude,
        trace_accel,
        trace_predicted_apogee,
        trace_servo_control,
        trace_average_altitude,
    ],
    layout=layout,
)

# annotate the state changes on the altitude plot
for state_change in state_changes:
    y = df["altitude"][state_change[0]]
    fig.add_annotation(
        x=state_change[0],
        y=y,
        text=state_change[1],
        showarrow=True,
        arrowhead=7,
        ax=0,
        ay=-75,
    )

# Show the plot
fig.show()
