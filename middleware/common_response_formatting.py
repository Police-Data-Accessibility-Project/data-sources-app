from flask import Response, make_response


def format_list_response(data: dict, message: str = "") -> dict:
    data.update({"message": message})
    return data


def multiple_results_response(data: list, message: str = "") -> Response:
    """
    Format a list of dictionaries into a dictionary with the count and data keys.
    Args:
        data (list): A list of dictionaries to format.
    Returns:
        dict: A dictionary with the count and data keys.
    """
    return make_response(format_list_response(data=data, message=message))


def created_id_response(new_id: str, message: str = "") -> Response:
    return message_response(message=message, id=new_id)


def message_response(message: str, **kwargs) -> Response:
    """Format response with standardized message format.
    :param message:
    :param kwargs:
    """

    dict_response = {"message": message}
    dict_response.update(kwargs)
    return make_response(dict_response)
