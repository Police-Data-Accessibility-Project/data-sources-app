import uuid
from http import HTTPStatus

from flask import Response, make_response
from flask_restx import abort
from werkzeug.security import check_password_hash

from database_client.database_client import DatabaseClient
from database_client.helper_functions import get_db_client
from middleware.access_logic import get_api_key_from_request_header
from middleware.api_key import ApiKey
from middleware.exceptions import (
    InvalidAPIKeyException,
    InvalidAuthorizationHeaderException,
)
from middleware.primary_resource_logic.user_queries import UserRequestDTO
import hashlib


def generate_api_key() -> str:
    return uuid.uuid4().hex


def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()


def create_api_key_for_user(db_client: DatabaseClient, dto: UserRequestDTO) -> Response:
    """
    Tries to log in a user. If successful, generates API key

    :param db_client: A DatabaseClient object.
    :param email: User's email.
    :param password: User's password.
    :return: A response object with a message and status code.
    """
    user_data = db_client.get_user_info(dto.email)

    if check_password_hash(user_data.password_digest, dto.password):
        api_key = ApiKey()
        db_client.update_user_api_key(user_id=user_data.id, api_key=api_key.key_hash)
        payload = {"api_key": api_key.raw_key}
        return make_response(payload, HTTPStatus.OK)

    return make_response(
        {"message": "Invalid email or password"}, HTTPStatus.UNAUTHORIZED
    )


def api_key_is_associated_with_user(db_client: DatabaseClient, raw_key: str) -> bool:
    api_key = ApiKey(raw_key)
    user_identifiers = db_client.get_user_by_api_key(api_key.key_hash)
    return user_identifiers is not None


def check_api_key_associated_with_user(db_client: DatabaseClient, raw_key: str) -> None:
    is_associated_with_user = api_key_is_associated_with_user(db_client, raw_key)
    if not is_associated_with_user:
        abort(HTTPStatus.UNAUTHORIZED, "Invalid API Key")


INVALID_API_KEY_MESSAGE = "Please provide an API key in the request header in the 'Authorization' key with the format 'Basic <api_key>'"


def check_api_key() -> None:
    try:
        api_key = get_api_key_from_request_header()
        db_client = get_db_client()
        check_api_key_associated_with_user(db_client, api_key)
    except (InvalidAPIKeyException, InvalidAuthorizationHeaderException):
        abort(code=HTTPStatus.UNAUTHORIZED, message=INVALID_API_KEY_MESSAGE)
