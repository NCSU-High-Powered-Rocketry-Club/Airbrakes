import pandas as pd
import plotly.graph_objects as go

# Run this file after you have run the simulation (python .\main.py -si)

filename = "simulation.csv"

# Read data using pandas
df = pd.read_csv(filename)

# Create traces for Altitude and Acceleration
trace_altitude = go.Scatter(x=df['timestamp'], y=df['altitude'], mode='lines', name='Altitude', line=dict(color='blue'))
trace_accel = go.Scatter(x=df['timestamp'], y=df['accel'], mode='lines', name='Acceleration', line=dict(color='red'))

# Create layout
layout = go.Layout(title="Simulation Data Over Time", xaxis=dict(title='Time'), yaxis=dict(title='Simulation Data'))

# Create figure
fig = go.Figure(data=[trace_altitude, trace_accel], layout=layout)

# Show the plot
fig.show()
