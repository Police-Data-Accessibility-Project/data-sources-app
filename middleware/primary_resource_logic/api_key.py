import hashlib
import uuid

from flask import Response, make_response
from werkzeug.exceptions import Unauthorized

from db.client.core import DatabaseClient
from middleware.exceptions import (
    InvalidAPIKeyException,
    InvalidAuthorizationHeaderException,
)
from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.security.api_key.core import ApiKey
from middleware.security.api_key.helpers import get_token_from_request_header
from middleware.security.auth.method_config.enums import AuthScheme


def generate_token() -> str:
    return uuid.uuid4().hex


def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()


def create_api_key_for_user(
    db_client: DatabaseClient, access_info: AccessInfoPrimary
) -> Response:
    """
    Tries to log in a user. If successful, generates API key

    :param db_client: A DatabaseClient object.
    :param email: User's email.
    :param password: User's password.
    :return: A response object with a message and status code.
    """
    user_id = access_info.get_user_id()

    api_key = ApiKey()
    db_client.update_user_api_key(user_id=user_id, api_key=api_key.key_hash)
    return make_response({"api_key": api_key.raw_key})


def api_key_is_associated_with_user(db_client: DatabaseClient, raw_key: str) -> bool:
    api_key = ApiKey(raw_key)
    user_identifiers = db_client.get_user_by_api_key(api_key.key_hash)
    return user_identifiers is not None


def check_api_key_associated_with_user(db_client: DatabaseClient, raw_key: str) -> None:
    is_associated_with_user = api_key_is_associated_with_user(db_client, raw_key)
    if not is_associated_with_user:
        raise Unauthorized("Invalid API Key")


INVALID_API_KEY_MESSAGE = "Please provide an API key in the request header in the 'Authorization' key with the format 'Basic <api_key>'"


def check_api_key() -> None:
    try:
        api_key = get_token_from_request_header(scheme=AuthScheme.BASIC)
        db_client = DatabaseClient()
        check_api_key_associated_with_user(db_client, api_key)
    except (InvalidAPIKeyException, InvalidAuthorizationHeaderException):
        raise Unauthorized(INVALID_API_KEY_MESSAGE)
