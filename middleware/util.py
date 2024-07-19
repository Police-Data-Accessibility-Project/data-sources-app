import os

from dotenv import dotenv_values, find_dotenv


def get_env_variable(name: str) -> str:
    """
    Get the value of the specified environment variable.
    Args:
        name (str): The name of the environment variable to retrieve.
    Returns:
        str: The value of the specified environment variable.
    Raises:
        ValueError: If the environment variable is not set or is empty.
    """
    env_vars = dotenv_values(find_dotenv())
    value = os.getenv(name, env_vars.get(name))
    if value is None or value == "":
        raise ValueError(f"Environment variable '{name}' is not set or is empty.")
    return value


def format_list_response(data: list) -> dict:
    """
    Format a list of dictionaries into a dictionary with the count and data keys.
    Args:
        data (list): A list of dictionaries to format.
    Returns:
        dict: A dictionary with the count and data keys.
    """
    return {"count": len(data), "data": data}
