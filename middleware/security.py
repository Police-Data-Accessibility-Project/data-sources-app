import functools
from flask import request, jsonify
from flask_restx import abort


from collections import namedtuple

from http import HTTPStatus
from flask import request

from database_client.database_client import DatabaseClient
from middleware.initialize_psycopg2_connection import initialize_psycopg2_connection
from datetime import datetime as dt
from middleware.login_queries import is_admin
from typing import Tuple, Optional

APIKeyStatus = namedtuple("APIKeyStatus", ["is_valid", "is_expired"])


class NoAPIKeyError(Exception):
    pass


class ExpiredAPIKeyError(Exception):
    pass


class InvalidAPIKeyError(Exception):
    pass


class InvalidRoleError(Exception):
    pass


def validate_api_key(api_key: str, endpoint: str, method: str):
    """
    Validates the API key and checks if the user has the required role to access a specific endpoint.

    :param api_key: The API key provided by the user.
    :param endpoint: The endpoint the user is trying to access.
    :param method: The HTTP method of the request.
    :return: A tuple (isValid, isExpired) indicating whether the API key is valid and not expired.
    """

    psycopg2_connection = initialize_psycopg2_connection()
    cursor = psycopg2_connection.cursor()
    db_client = DatabaseClient(cursor)
    role = get_role(api_key, db_client)
    if role:
        validate_role(role, endpoint, method)
        return

    try:
        session_token_results = get_session_token(api_key, db_client)

        if session_token_results.expiration_date < dt.utcnow():
            raise ExpiredAPIKeyError("Session token expired")

        if is_admin(cursor, session_token_results.email):
            validate_role(role="admin", endpoint=endpoint, method=method)
            return

    except SessionTokenNotFoundError:
        delete_expired_access_tokens(cursor, psycopg2_connection)
        try:
            # TODO: Replace with DatabaseClient method get_access_token()
            get_access_token(api_key, cursor)
            role = "user"
        except AccessTokenNotFoundError:
            raise InvalidAPIKeyError("API Key not found")

    validate_role(role, endpoint, method)


def validate_role(role: str, endpoint: str, method: str):
    # Compare the API key in the user table to the API in the request header and proceed
    # through the protected route if it's valid. Otherwise, compare_digest will return False
    # and api_required will send an error message to provide a valid API key
    if is_admin_only_action(endpoint, method) and role != "admin":
        raise InvalidRoleError("You do not have permission to access this endpoint")


def get_role(api_key, db_client: DatabaseClient) -> Optional[str]:
    role = db_client.get_role_by_api_key(api_key)
    if role is None:
        return None
    if role.role is None:
        return "user"
    return role.role



SessionTokenResults = namedtuple("SessionTokenResults", ["email", "expiration_date"])


class SessionTokenNotFoundError(Exception):
    pass


def get_session_token(api_key, db_client: DatabaseClient) -> SessionTokenResults:
    session_token_results = db_client.get_session_token_info(api_key)
    if not session_token_results:
        raise SessionTokenNotFoundError("Session token not found")
    return session_token_results


class AccessTokenNotFoundError(Exception):
    pass


# DatabaseClient.get_access_token()
def get_access_token(api_key, cursor) -> str:
    cursor.execute(f"select id, token from access_tokens where token = %s", (api_key,))
    results = cursor.fetchone()
    if not results:
        raise AccessTokenNotFoundError("Access token not found")
    return results[1]


def delete_expired_access_tokens(cursor, psycopg2_connection):
    cursor.execute(f"delete from access_tokens where expiration_date < NOW()")
    psycopg2_connection.commit()


def is_admin_only_action(endpoint, method):
    return endpoint in ("datasources", "datasourcebyid") and method in ("PUT", "POST")


class InvalidHeader(Exception):

    def __init__(self, message: str):
        super().__init__(message)


def validate_header() -> str:
    """
    Validates the API key and checks if the user has the required role to access a specific endpoint.
    :return:
    """
    if not request.headers or "Authorization" not in request.headers:
        raise InvalidHeader(
            "Please provide an 'Authorization' key in the request header"
        )

    authorization_header = request.headers["Authorization"].split(" ")
    if len(authorization_header) < 2 or authorization_header[0] != "Bearer":
        raise InvalidHeader(
            "Please provide a properly formatted bearer token and API key"
        )

    api_key = authorization_header[1]
    if api_key == "undefined":
        raise InvalidHeader("Please provide an API key")
    return api_key


def validate_token() -> Optional[Tuple[dict, int]]:
    """
    Validates the API key and checks if the user has the required role to access a specific endpoint.
    :return:
    """
    try:
        api_key = validate_header()
    except InvalidHeader as e:
        return {"message": str(e)}, HTTPStatus.BAD_REQUEST.value
    # Check if API key is correct and valid
    try:
        validate_api_key(api_key, request.endpoint, request.method)
    except ExpiredAPIKeyError as e:
        return {"message": str(e)}, HTTPStatus.UNAUTHORIZED.value
    except InvalidRoleError as e:
        return {"message": str(e)}, HTTPStatus.FORBIDDEN.value

    return None


def api_required(func):
    """
    The api_required decorator can be added to protect a route so that only authenticated users can access the information
    To protect a route with this decorator, add @api_required on the line above a given route
    The request header for a protected route must include an "Authorization" key with the value formatted as "Bearer [api_key]"
    A user can get an API key by signing up and logging in (see User.py)
    """

    @functools.wraps(func)
    def decorator(*args, **kwargs):
        validation_error = validate_token()
        if validation_error:
            return validation_error
        return func(*args, **kwargs)

    return decorator
