import concurrent.futures
import csv
import sys
import subprocess
import os


VELOCITY_STEP = 100
# EXTENSIONS = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
EXTENSIONS = [0.0, 0.5, 1.0]
FILEPATH = "lookup_table.csv"


def get_newest_log_lines() -> list[str]:
    # Read the log file
    if len(sys.argv) < 2:
        # Get the newest file from the logs folder
        logs = os.listdir("./logs")
        logs.sort()
        filename = "./logs/" + logs[-1]
    else:
        filename = sys.argv[1]

    with open(filename, "r") as file:
        return file.readlines()


def get_log_lines(file_path: str) -> list[str]:
    with open(file_path, "r") as file:
        return file.readlines()


def get_control_state_index(lines) -> int:
    for i in range(len(lines)):
        parts = lines[i].strip().split(",")
        if parts[2] == "ControlState":
            return i


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
        # Checks for reaching apogee
        if current_altitude <= last_altitude:
            print("apogee " + str(current_altitude))
            return current_altitude - deploy_altitude
        last_altitude = current_altitude


def launch_sim(deploy_velocity: float = 0, extension_percent: float = 0) -> None:
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


def write_lookup_table_to_csv(file_path: str, lookup_table: list):
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Initial Velocity", "Extension Lookup Table"])
        for row in lookup_table:
            x_value, y_values = row
            writer.writerow([x_value, y_values])


def read_lookup_table_from_csv(file_path: str) -> list:
    read_data = []
    with open(file_path, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header row
        for row in reader:
            x_value = int(row[0])
            y_values = eval(row[1])  # Use eval to convert string representation of list to list
            read_data.append([x_value, y_values])
        return read_data


def main():
    lookup_table = []

    # Runs the sim once to get some starting values
    launch_sim()
    log_lines = get_newest_log_lines()
    control_state_index = get_control_state_index(log_lines)
    max_velocity = float(log_lines[control_state_index + 1].split(",")[4])

    # Makes the skeleton lookup table
    lookup_table = [
        [float(velocity), [[extension, 0] for extension in EXTENSIONS]]
        for velocity in range(int(max_velocity), 0, -VELOCITY_STEP)
    ]

    for velocity_entry in lookup_table:
        velocity = velocity_entry[0]
        for extension_entry in velocity_entry:
            extension = extension_entry[0]
            lines = get_log_lines(f"logs/lookup_table_logs/vel{velocity}ext{extension}.log")
            change_in_altitude = get_change_in_altitude(lines, velocity)
            extension_entry[1] = change_in_altitude



if __name__ == "__main__":
    # main()
    vel = 100.0
    ext = .5
    # launch_sim(vel, ext)
    filepath = f"logs/lookup_table_logs/vel{vel}ext{ext}.log"
