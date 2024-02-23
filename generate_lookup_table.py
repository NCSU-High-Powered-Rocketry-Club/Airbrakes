import sys
import pandas as pd
import plotly.graph_objects as go
from AirbrakeSystem import airbrakes

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

