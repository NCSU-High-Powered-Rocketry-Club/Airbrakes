import matplotlib.pyplot as plt
import csv

filename = "simulation.csv"
headers = ["timestamp", "altitude", "accel"]
timestamps: [float] = []
altitudes: [float] = []
accels: [float] = []

with open(filename, "r") as file:
    csvreader = csv.reader(file)
    header = next(csvreader)
    for row in csvreader:
        timestamps.append(float(row[0]))
        altitudes.append(float(row[1]))
        accels.append(float(row[2]))

plt.plot(timestamps, altitudes)
plt.plot(timestamps, accels)

plt.show()
