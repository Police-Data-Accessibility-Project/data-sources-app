"""
This FlaskResponseManager is a wrapper class designed to consolidate calls to make_response and abort
through a single point of entry, which can be mocked as well as enable additional
logic to be added as necessary.
"""

from http import HTTPStatus
from typing import Optional, Type

from flask import make_response, Response
from marshmallow import Schema, ValidationError
from werkzeug.exceptions import InternalServerError


def validate_data_with_schema(data, validation_schema):
    try:
        validation_schema().load(data)
    except ValidationError as e:
        raise InternalServerError(f"Error validating response schema: {e}")
