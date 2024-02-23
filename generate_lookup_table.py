import csv
import numpy as np
import sys
import subprocess
import os

# Okay I know this is not very efficient but who cares

VELOCITY_STEP = 100
EXTENSIONS = [0, 0.5]


def get_newest_log_lines() -> list[str]:
    # Read the log file
    if len(sys.argv) < 2:
        # Get the newest file from the logs folder
        import os
        logs = os.listdir("./logs")
        logs.sort()
        filename = "./logs/" + logs[-1]
    else:
        filename = sys.argv[1]

    with open(filename, "r") as file:
        return file.readlines()


def get_change_in_altitude(lines, deploy_velocity) -> float:
    last_altitude = 0
    deploy_altitude = None
    for i in range(0, len(lines)):
        parts = lines[i].strip().split(",")
        if parts[1] != "Data point":
            continue
        current_altitude = float(parts[2])
        if deploy_altitude is None and float(parts[4]) <= deploy_velocity:
            deploy_altitude = current_altitude
            print("deploy " + str(deploy_altitude))
        # Checks for reaching apogee
        if current_altitude <= last_altitude:
            print("apogee " + str(current_altitude))
            return current_altitude - deploy_altitude
        last_altitude = current_altitude


def get_control_state_index(lines) -> int:
    for i in range(len(lines)):
        parts = lines[i].strip().split(",")
        if parts[2] == "ControlState":
            return i


def launch_sim(deploy_velocity: float = 0, extension_percent: float = 0):
    file_path = "main.py"
    # Arguments to pass to the Python script
    script_args = ["-si", "-v", str(deploy_velocity), "-e", str(extension_percent)]
    venv_dir = ".venv"
    # Activate the virtual environment
    venv_activate = os.path.join(venv_dir, "Scripts", "activate") if sys.platform == "win32" else os.path.join(venv_dir, "bin", "activate")
    try:
        # Run the activate command
        activate_cmd = f"call {venv_activate}" if sys.platform == "win32" else f"source {venv_activate}"
        subprocess.run(activate_cmd, shell=True, check=True)
        # Run the Python script externally with arguments and capture its output
        process = subprocess.Popen([sys.executable, file_path] + script_args, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True)
        process.communicate()
        # # Read and print the output
        # print("Standard Output:")
        # print(stdout)
        # print("Standard Error:")
        # print(stderr)

        # Check if the process exited successfully
        if process.returncode == 0:
            print("File executed successfully.")
        else:
            print("Failed to execute the file.")
    except FileNotFoundError:
        print("File not found or command not found.")
    except OSError as e:
        print(f"Error starting the process: {e}")


# Initialize lookup table
lookup_table = []

# Runs the sim once to get some starting values
launch_sim()
log_lines = get_newest_log_lines()
control_state_index = get_control_state_index(log_lines)
max_velocity = float(log_lines[control_state_index + 1].split(",")[4])

# Runs the simulations to get the values for the lookup table
for velocity in range(int(max_velocity), 0, -VELOCITY_STEP):
    velocity_entry = [velocity, []]
    for extension in EXTENSIONS:
        extension_entry = [extension]
        launch_sim(velocity, extension)
        log_lines = get_newest_log_lines()
        print("vel " + str(velocity))
        extension_entry.append(get_change_in_altitude(log_lines[control_state_index + 1:], velocity))
        velocity_entry[1].append(extension_entry)
    lookup_table.append(velocity_entry)


print(lookup_table)

flattened_data = []
for entry in lookup_table:
    first_value = entry[0]
    for sublist in entry[1]:
        flattened_data.append([first_value] + sublist)

# Write flattened data to CSV file
with open('data.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['First Value', 'Second Value', 'Third Value'])
    for row in flattened_data:
        writer.writerow(row)



# Read data from CSV file into a list
read_data = []
with open('data.csv', 'r', newline='') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)  # Skip header row
    for row in reader:
        read_data.append(row)

# Reconstruct the original structure
reconstructed_data = []
for row in read_data:
    first_value = int(row[0])
    sublist = [[float(row[1]), float(row[2])]]
    reconstructed_data.append([first_value, sublist])

print(reconstructed_data)