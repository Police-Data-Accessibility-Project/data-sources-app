"""
This FlaskResponseManager is a wrapper class designed to consolidate calls to make_response and abort
through a single point of entry, which can be mocked as well as enable additional
logic to be added as necessary.
"""

from http import HTTPStatus
from typing import Optional, Type

from flask import make_response, Response, redirect
from flask_restx import abort
from marshmallow import Schema, ValidationError


class FlaskResponseManager:

    @classmethod
    def make_response(
        cls,
        data: dict,
        status_code: HTTPStatus = HTTPStatus.OK,
        validation_schema: Optional[Type[Schema]] = None,
    ) -> Response:
        if validation_schema is not None:
            cls.validate_data_with_schema(data, validation_schema)
        return make_response(data, status_code)

    @classmethod
    def validate_data_with_schema(cls, data, validation_schema):
        try:
            validation_schema().load(data)
        except ValidationError as e:
            abort(
                code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Error validating response schema: {e}",
            )

    @classmethod
    def abort(cls, code: int, message: str) -> Response:
        abort(code=code, message=message)

    @classmethod
    def redirect(cls, url: str, data: Optional[dict]) -> Response:
        if data is not None:
            response = make_response(data, HTTPStatus.FOUND)
            return redirect(url, code=HTTPStatus.FOUND, Response=response)
        return redirect(url, code=HTTPStatus.FOUND)

    @classmethod
    def permission_denied_abort(cls) -> None:
        abort(
            code=HTTPStatus.FORBIDDEN,
            message="You do not have permission to access this endpoint",
        )

    @classmethod
    def bad_request_abort(
        cls, message: str = "Improperly formatted authorization header"
    ) -> None:
        return abort(code=HTTPStatus.BAD_REQUEST, message=message)
