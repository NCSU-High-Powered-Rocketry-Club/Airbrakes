import main
import argparse
import sys

# Okay I know this is not very efficient but who cares

VELOCITY_STEP = 10
EXTENSIONS = [0.5]


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
        # Checks for reaching apogee
        if current_altitude <= last_altitude:
            return current_altitude - deploy_altitude
        last_altitude = current_altitude


def get_control_state_index(lines) -> int:
    for i in range(len(lines)):
        parts = lines[i].strip().split(",")
        if parts[2] == "ControlState":
            return i

lookup_table = [
    # Initial Velocity, [(Extensions, Change in Altitude)]
]

log_lines = get_newest_log_lines()

control_state_index = get_control_state_index(log_lines)
# The max vel in the lookup table will be right after the control state starts
max_velocity = float(log_lines[control_state_index + 1].split(",")[4])
print(get_change_in_altitude(log_lines[control_state_index + 1:], max_velocity))

# # Runs the simulations to get the values for the lookup table
# for velocity in range(int(get_max_velocity()), 0, -VELOCITY_STEP):
#     velocity_entry = [velocity, []]
#     for extension in EXTENSIONS:
#         extension_entry = [extension]
#         args_list = ["-si", "-v", str(velocity), "-e", extension]
#         args = argparse.Namespace()
#         main.parser.parse_args(args_list, namespace=args)
#         main.main(args)

