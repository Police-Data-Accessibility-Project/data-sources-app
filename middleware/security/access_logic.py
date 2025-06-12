from http import HTTPStatus

from flask import request

from middleware.flask_response_manager import FlaskResponseManager


def get_authorization_header_from_request() -> str:
    headers = request.headers
    try:
        return headers["Authorization"]
    except (KeyError, TypeError):
        FlaskResponseManager.abort(
            code=HTTPStatus.BAD_REQUEST, message="Authorization header missing"
        )
