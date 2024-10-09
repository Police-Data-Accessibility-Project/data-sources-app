import os
from dataclasses import is_dataclass, asdict
from enum import Enum
from typing import Any, Dict

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


def get_enum_values(en: type[Enum]):
    return [e.value for e in en]

def dataclass_to_filtered_dict(instance: Any) -> Dict[str, Any]:
    """
    Convert a dataclass instance to a dictionary, filtering out any None values.
    :param instance:
    :return:
    """
    if not is_dataclass(instance):
        raise TypeError(f"Expected a dataclass instance, but got {type(instance).__name__}")
    return {key: value for key, value in asdict(instance).items() if value is not None}