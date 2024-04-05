import concurrent.futures
import csv
import sys
import subprocess
import os
import time


VELOCITY_STEP = 1  # Keep this at 1 for quick look up table indexing
FILEPATH = "AirbrakeSystem/lookup_table.csv"
# This will only be used for when we do apogee estimation for PID control
EXTENSIONS = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]


def get_log_lines(file_path: str = "logs/lookup_table_logs/vel0.0ext0.0.log") -> list[str]:
    with open(file_path, "r") as file:
        return file.readlines()


def get_control_state_index(lines: list[str]) -> int:
    for i in range(len(lines)):
        parts = lines[i].strip().split(",")
        if parts[2] == "ControlState":
            return i


def get_change_in_altitude(lines: list[str], current_velocity: float) -> float:
    last_altitude = 0
    deploy_altitude = None
    for i in range(0, len(lines)):
        parts = lines[i].strip().split(",")
        if parts[1] != "Data point":
            continue
        current_altitude = float(parts[2])
        if deploy_altitude is None and float(parts[4]) <= current_velocity:
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

        # Use .communicate() instead of .wait() as it will cause a deadlock
        process.communicate()

        # Check if the process exited successfully
        if process.returncode == 0:
            print(f"Simulation with a velocity {deploy_velocity} and an extension {extension_percent} ran successfully.")
        else:
            print("Simulation failed.")
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


def generate_pid_lookup_table(max_velocity: float, control_state_index: int):
    # Makes the skeleton lookup table
    lookup_table = [
        [float(velocity), [[extension, 0.0] for extension in EXTENSIONS]]
        for velocity in range(int(max_velocity), 0, -VELOCITY_STEP)
    ]

    # Create a thread pool
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit tasks to the thread pool
        futures = []
        for i in range(len(lookup_table)):
            velocity = lookup_table[i][0]
            for j in range(len(lookup_table[i][1])):
                extension = lookup_table[i][1][j][0]
                future = executor.submit(launch_sim, velocity, extension)
                futures.append(future)

    # Wait for all tasks to complete
    concurrent.futures.wait(futures)

    # Fills up the lookup table
    for i in range(len(lookup_table)):
        velocity = lookup_table[i][0]
        for j in range(len(lookup_table[i][1])):
            extension = lookup_table[i][1][j][0]
            lines = get_log_lines(f"logs/lookup_table_logs/vel{velocity}ext{extension}.log")
            # Only gets the lines after the control state
            lines = lines[control_state_index + 1:]
            change_in_altitude = get_change_in_altitude(lines, velocity)
            lookup_table[i][1][j][1] = change_in_altitude

    print(lookup_table)

    write_lookup_table_to_csv("AirbrakeSystem/pid_lookup_table.csv", lookup_table)


def generate_bang_bang_lookup_table(log_lines: list[str], control_state_index: int):
    control_lines = log_lines[control_state_index + 1:]
    lookup_table = []
    for line in control_lines:
        if line.split(",")[1] != "Data point":
            continue
        velocity = float(line.split(",")[4])
        if velocity > 0:
            lookup_table.append([velocity, get_change_in_altitude(control_lines, velocity)])
        else:
            break

        print(lookup_table)

        write_lookup_table_to_csv("AirbrakeSystem/bang_bang_lookup_table.csv", lookup_table)


def main():
    # Runs the sim once to get some starting values
    launch_sim()
    log_lines = get_log_lines()
    control_state_index = get_control_state_index(log_lines)
    max_velocity = float(log_lines[control_state_index + 1].split(",")[4])

    # This took my computer about 30 minutes
    # generate_pid_lookup_table(max_velocity, control_state_index)

    # This took my computer 5 seconds
    generate_bang_bang_lookup_table(log_lines, control_state_index)


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print("lookup table generation took " + str(end_time - start_time) + "seconds")
