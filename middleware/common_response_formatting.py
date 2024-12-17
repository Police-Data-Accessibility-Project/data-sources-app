from http import HTTPStatus
from typing import Type, Optional

from flask import Response, make_response
from marshmallow import Schema

from middleware.constants import DATA_KEY
from middleware.flask_response_manager import FlaskResponseManager
from middleware.schema_and_dto_logic.common_response_schemas import (
    IDAndMessageSchema,
    GetManyResponseSchema,
)


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
    return FlaskResponseManager.make_response(
        format_list_response(data=data, message=message),
        HTTPStatus.OK,
    )


def created_id_response(new_id: str, message: str = "") -> Response:
    return message_response(
        message=message, id=new_id, validation_schema=IDAndMessageSchema
    )


def message_response(
    message: str,
    status_code: HTTPStatus = HTTPStatus.OK,
    validation_schema: Optional[Type[Schema]] = None,
    **kwargs
) -> Response:
    """
    Formats response with standardized message format
    :param message:
    :param status_code:
    :param kwargs:
    :return:
    """

    dict_response = {"message": message}
    dict_response.update(kwargs)
    status_code = status_code

    return FlaskResponseManager.make_response(
        data=dict_response, status_code=status_code, validation_schema=validation_schema
    )
