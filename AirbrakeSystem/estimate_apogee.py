import csv
import math


def load_sorted_lookup_table() -> list:
    read_data = []
    with open("lookup_table.csv", 'r', newline='') as csvfile:
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
    slope = (upper_y - lower_y) / (upper_x - lower_x)
    return (mid_x - lower_x) * slope + lower_y


def estimate_apogee(lookup_table: list, current_velocity: float, current_extension) -> float:
    max_velocity = lookup_table[-1][0]
    min_velocity = lookup_table[0][0]
    # Clamps the velocity to be within the lookup table
    current_velocity = max(min(current_velocity, max_velocity), min_velocity)
    # Because the velocities in the table have a step of 1, we can index it like this
    lower_velocity = math.floor(current_velocity)
    upper_velocity = math.ceil(current_velocity)
    lower_velocity_entry = lookup_table[lower_velocity - 1][1]
    upper_velocity_entry = lookup_table[upper_velocity - 1][1]
    lower_lower_extension, lower_upper_extension = get_bordering_extension_entries(lower_velocity_entry, current_extension)
    lower_interpolated_estimated_apogee = linearly_interpolate(
        lower_lower_extension[0],
        lower_lower_extension[1],
        lower_upper_extension[0],
        lower_upper_extension[1],
        current_extension
    )
    upper_lower_extension, upper_upper_extension = get_bordering_extension_entries(upper_velocity_entry, current_extension)
    upper_interpolated_estimated_apogee = linearly_interpolate(
        upper_lower_extension[0],
        upper_lower_extension[1],
        upper_upper_extension[0],
        upper_upper_extension[1],
        current_extension
    )
    interpolated_estimated_apogee = linearly_interpolate(
        lower_velocity,
        lower_interpolated_estimated_apogee,
        upper_velocity,
        upper_interpolated_estimated_apogee,
        current_velocity
    )
    return interpolated_estimated_apogee
