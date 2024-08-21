from dataclasses import dataclass
from http import HTTPStatus
from typing import Optional

from flask import request
from flask_jwt_extended import get_jwt_identity
from flask_restx import abort

from middleware.enums import PermissionsEnum, AccessTypeEnum
from database_client.helper_functions import get_db_client
from middleware.permissions_logic import get_user_permissions


class InvalidAPIKeyException(Exception):
    pass


class InvalidAuthorizationHeaderException(Exception):
    pass

JWT_OR_API_KEY_NEEDED_ERROR_MESSAGE = "Please provide an API key with the format 'Basic <api_key>' OR an access token with the format 'Bearer <access_token>' in the request header in the 'Authorization' key "

@dataclass
class AccessInfo:
    """
    A dataclass providing information on how the endpoint was accessed
    """
    user_email: str
    access_type: AccessTypeEnum
    permissions: list[PermissionsEnum] = None

def get_access_info_from_jwt_or_api_key() -> AccessInfo:
    user_email_api_key = get_user_email_from_api_key()
    if user_email_api_key is not None:
        return AccessInfo(
            user_email=user_email_api_key,
            access_type=AccessTypeEnum.API_KEY
        )
    user_email_jwt = get_jwt_identity()
    if user_email_jwt is not None:
        permissions = get_user_permissions(user_email_jwt)
        return AccessInfo(
            user_email=user_email_jwt,
            access_type=AccessTypeEnum.JWT,
            permissions=permissions
        )
    abort(
        code=HTTPStatus.UNAUTHORIZED,
        message=JWT_OR_API_KEY_NEEDED_ERROR_MESSAGE
    )

def get_user_email_from_api_key() -> Optional[str]:
    try:
        api_key = get_api_key_from_request_header()
    except (InvalidAPIKeyException, InvalidAuthorizationHeaderException):
        return None

    db_client = get_db_client()
    user_identifiers = db_client.get_user_by_api_key(api_key)
    return user_identifiers.email

def get_authorization_header_from_request() -> str:
    headers = request.headers
    try:
        return headers["Authorization"]
    except (KeyError, TypeError):
        raise InvalidAuthorizationHeaderException

def get_api_key_from_authorization_header(authorization_header: str) -> str:
    try:
        authorization_header_parts = authorization_header.split(" ")
        if authorization_header_parts[0] != "Basic":
            raise InvalidAPIKeyException
        return authorization_header_parts[1]
    except (ValueError, IndexError, AttributeError):
        raise InvalidAPIKeyException


def get_api_key_from_request_header() -> str:
    """
    Validates the API key and checks if the user has the required role to access a specific endpoint.
    :return:
    """
    authorization_header = get_authorization_header_from_request()
    return get_api_key_from_authorization_header(authorization_header)
