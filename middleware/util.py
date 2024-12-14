import csv
import os
from dataclasses import is_dataclass, asdict
from datetime import datetime
from enum import Enum
from io import BytesIO, StringIO
from typing import Any, Dict, TextIO, Generator

from dotenv import dotenv_values, find_dotenv
from pydantic import BaseModel
from werkzeug.datastructures import FileStorage


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


def get_datetime_now() -> str:
    return datetime.now().strftime("%Y-%m-%d-%H-%M-%S")


def create_web_app_url(endpoint: str) -> str:
    return f"{get_env_variable('VITE_VUE_APP_BASE_URL')}/{endpoint}"


def get_enum_values(en: type[Enum]) -> list[str]:
    return [e.value for e in en]


def write_to_csv(file_path: str, data: list[dict[str, Any]], fieldnames: list[str]):
    with open(file_path, "w+", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
        f.close()


def bytes_to_text_iter(file: BytesIO | FileStorage) -> Generator[str, Any, None]:
    """
    Convert BytesIO file to text iterator
    """
    return (line.decode("utf-8") for line in file)


def read_from_csv(file: str | FileStorage | bytes) -> list[dict[str, Any]]:
    if isinstance(file, FileStorage):
        file = bytes_to_text_iter(file)
    elif isinstance(file, str):
        file = open(file, "r", newline="", encoding="utf-8")
    elif isinstance(file, bytes):
        content = file.decode("utf-8")
        file = StringIO(content)
    return list(csv.DictReader(file))


def dict_enums_to_values(d: dict[str, Any]) -> dict[str, Any]:
    """
    Convert enums within a dictionary to their values.
    """
    for key, value in d.items():
        if isinstance(value, Enum):
            d[key] = value.value
    return d


def dataclass_to_filtered_dict(instance: Any) -> Dict[str, Any]:
    """
    Convert a dataclass instance to a dictionary, filtering out any None values.
    :param instance:
    :return:
    """
    if is_dataclass(instance):
        d = asdict(instance)
    elif isinstance(instance, BaseModel):
        d = dict(instance)
    else:
        raise TypeError(
            f"Expected a dataclass or basemodel instance, but got {type(instance).__name__}"
        )
    results = {}
    for key, value in d.items():
        # Special case for Enum
        if isinstance(value, Enum):
            results[key] = value.value
        # Special case for List of Enum
        elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], Enum):
            results[key] = [e.value for e in value]
        elif value is not None:
            results[key] = value
    return results


def update_if_not_none(dict_to_update: Dict[str, Any], secondary_dict: Dict[str, Any]):
    for key, value in secondary_dict.items():
        if value is not None:
            dict_to_update[key] = value


def find_root_directory(start_path=None, target_file="app.py"):
    """
    Travels upward from the given starting directory (or current working directory)
    until it finds the directory containing the specified target file.

    Parameters:
    - start_path (str): The directory to start searching from. Defaults to the current working directory.
    - target_file (str): The file that identifies the root directory. Defaults to 'app.py'.

    Returns:
    - str: The absolute path to the root directory containing the target file.

    Raises:
    - FileNotFoundError: If the target file is not found in any parent directory.
    """
    current_path = os.path.abspath(start_path or os.getcwd())

    while True:
        if os.path.isfile(os.path.join(current_path, target_file)):
            return current_path

        parent_path = os.path.dirname(current_path)
        if current_path == parent_path:  # Reached the root of the filesystem
            break
        current_path = parent_path

    raise FileNotFoundError(f"Could not find '{target_file}' in any parent directory.")


def get_temp_directory() -> str:
    # Go to root directory

    return os.path.join(os.getcwd(), "temp")


def stringify_list_of_ints(l: list[int]):
    for i in range(len(l)):
        l[i] = str(l[i])
    return l


def stringify_lists(d: dict):
    for k, v in d.items():
        if isinstance(v, dict):
            stringify_lists(v)
        if isinstance(v, list):
            v = stringify_list_of_ints(v)
            d[k] = ",".join(v)
    return d
