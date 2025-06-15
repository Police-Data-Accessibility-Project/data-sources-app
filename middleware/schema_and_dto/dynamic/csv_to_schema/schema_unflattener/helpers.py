from typing import Any


def set_nested_value(d: dict, path: list[str], value: Any):
    """
    Sets a value in a nested dictionary based on a given path.
    Creates nested dictionaries for intermediate keys if they don't exist.

    :param d: The dictionary to modify.
    :param path: A list of strings representing the path to the desired key.
    :param value: The value to set for the final key.
    """
    current = d
    for key in path[:-1]:  # Iterate over all keys except the last one
        if key not in current:
            current[key] = {}  # Create a new dictionary if key is missing
        current = current[key]
    current[path[-1]] = value
