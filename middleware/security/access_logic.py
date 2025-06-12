from flask import request
from werkzeug.exceptions import BadRequest


def get_authorization_header_from_request() -> str:
    headers = request.headers
    try:
        return headers["Authorization"]
    except (KeyError, TypeError):
        raise BadRequest("Authorization header missing")
