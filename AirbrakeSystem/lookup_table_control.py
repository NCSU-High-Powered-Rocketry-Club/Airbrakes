import csv
import math


def load_sorted_pid_lookup_table() -> list:
    """
    Loads the lookup table that was generated with generate_lookup_table.py.
    It is sorted by velocities in ascending order.
    :return: [[vel1, [[ext1, est_change_in_altitude1], [ext2, est_change_in_altitude2]...]], [vel2, ...]]
    """
    read_data = []
    with open("AirbrakeSystem/lookup_table.csv", 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header row
        for row in reader:
            x_value = float(row[0])
            y_values = eval(row[1])  # Use eval to convert string representation of list to list
            read_data.append([x_value, y_values])
        return read_data[::-1]


def get_bordering_extension_entries(extension_entries: list, current_extension: float) -> list:
    """
    Gets the extension entries below and above the current extension
    :param extension_entries: the upper or lower extension entries list
    :param current_extension: the current extension of the airbrakes
    :return: [lower_extension_entry, upper_extension_entry]
    """
    # To be safe, has default values for max extension
    bordering_extension_entries = [extension_entries[-2], extension_entries[-1]]
    for i in range(len(extension_entries)):
        extension = extension_entries[i][0]
        if current_extension < extension:
            bordering_extension_entries = [extension_entries[i - 1], extension_entries[i]]
            break
    return bordering_extension_entries


def linearly_interpolate(lower_x: float, lower_y: float, upper_x: float, upper_y: float, mid_x: float) -> float:
    """
    Estimates a value between two points via linear interpolation
    :return: the y value corresponding to mid_x
    """
    if upper_x - lower_x == 0:
        slope = 0
    else:
        slope = (upper_y - lower_y) / (upper_x - lower_x)
    return (mid_x - lower_x) * slope + lower_y


def estimate_change_in_altitude(lookup_table: list, current_velocity: float, current_extension) -> float:
    """
    Estimates the change in altitude of the rocket based on its current 
    velocity and current airbrake extension.
    :param lookup_table: the lookup table to use for estimation
    :param current_velocity: the current velocity in m/s
    :param current_extension: the current airbrake extension from 0.0 to 1.0
    :return: the estimated change in altitude
    """
    max_velocity = lookup_table[-1][0]
    min_velocity = lookup_table[0][0]
    # Clamps the velocity to be within the lookup table
    current_velocity = max(min(current_velocity, max_velocity), min_velocity)
    # Because the velocities in the table have a step of 1, we can index it like this
    lower_velocity = math.floor(current_velocity)
    upper_velocity = math.ceil(current_velocity)
    lower_velocity_entry = lookup_table[lower_velocity - 1][1]
    upper_velocity_entry = lookup_table[upper_velocity - 1][1]
    # Gets the interpolated value between extension entries for the lower velocity
    lower_lower_extension, lower_upper_extension = get_bordering_extension_entries(lower_velocity_entry, current_extension)
    lower_interpolated_change_in_altitude = linearly_interpolate(
        lower_lower_extension[0],
        lower_lower_extension[1],
        lower_upper_extension[0],
        lower_upper_extension[1],
        current_extension
    )
    # Gets the interpolated value between extension entries for the upper velocity
    upper_lower_extension, upper_upper_extension = get_bordering_extension_entries(upper_velocity_entry, current_extension)
    upper_interpolated_change_in_altitude = linearly_interpolate(
        upper_lower_extension[0],
        upper_lower_extension[1],
        upper_upper_extension[0],
        upper_upper_extension[1],
        current_extension
    )
    # Gets the interpolated value between the upper and lower velocity
    interpolated_change_in_altitude = linearly_interpolate(
        lower_velocity,
        lower_interpolated_change_in_altitude,
        upper_velocity,
        upper_interpolated_change_in_altitude,
        current_velocity
    )
    return interpolated_change_in_altitude


def load_bang_bang_lookup_table() -> list:
    """
    Loads the lookup table that was generated with generate_lookup_table.py for a bang bang controller.
    It is sorted by velocities in ascending order.
    :return: [[vel1, change_in_alt1], [vel2, change_in_alt2]...]
    """
    read_data = []
    with open("AirbrakeSystem/bang_bang_lookup_table.csv", 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header row
        for row in reader:
            velocity = float(row[0])
            change_in_altitude = float(row[1])
            read_data.append([velocity, change_in_altitude])
        return read_data[::-1]


def get_bang_bang_change_in_altitude(lookup_table: list, current_velocity: float) -> float:
    for i in range(len(lookup_table) - 1):
        if lookup_table[i][0] < current_velocity < lookup_table[i + 1][0]:
            return linearly_interpolate(lookup_table[i][0], lookup_table[i][1],
                                        lookup_table[i + 1][0], lookup_table[i + 1][1], current_velocity)
