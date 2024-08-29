import os
from http import HTTPStatus

from dotenv import dotenv_values, find_dotenv
from flask import Response, make_response

from middleware.constants import DATA_KEY


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


def format_list_response(data: list, message: str = "") -> dict:
    """
    Format a list of dictionaries into a dictionary with the count and data keys.
    Args:
        data (list): A list of dictionaries to format.
    Returns:
        dict: A dictionary with the count and data keys.
    """
    return {
        "message": message,
        "count": len(data),
        DATA_KEY: data
    }

def multiple_results_response(data: list, message: str = "") -> Response:
    """
    Format a list of dictionaries into a dictionary with the count and data keys.
    Args:
        data (list): A list of dictionaries to format.
    Returns:
        dict: A dictionary with the count and data keys.
    """
    return make_response(
        format_list_response(data=data, message=message),
        HTTPStatus.OK
    )

def created_id_response(new_id: str, message: str = "") -> Response:
    return message_response(message=message, id=new_id)

def message_response(message: str, status_code: HTTPStatus = HTTPStatus.OK, **kwargs) -> Response:
    """
    Formats response with standardized message format
    :param message:
    :param status_code:
    :param kwargs:
    :return:
    """

    dict_response = {
        "message": message
    }
    dict_response.update(kwargs)
    status_code = status_code

    return make_response(
        dict_response,
        status_code
    )


