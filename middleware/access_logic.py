from dataclasses import dataclass
from http import HTTPStatus
from typing import Optional

from flask import request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from flask_restx import abort

from middleware.enums import PermissionsEnum, AccessTypeEnum
from database_client.helper_functions import get_db_client
from middleware.exceptions import InvalidAPIKeyException, InvalidAuthorizationHeaderException
from middleware.permissions_logic import get_user_permissions

JWT_OR_API_KEY_NEEDED_ERROR_MESSAGE = "Please provide an API key with the format 'Basic <api_key>' OR an access token with the format 'Bearer <access_token>' in the request header in the 'Authorization' key "


@dataclass
class AccessInfo:
    """
    A dataclass providing information on how the endpoint was accessed
    """

    user_email: str
    access_type: AccessTypeEnum
    permissions: list[PermissionsEnum] = None

def get_access_info_from_jwt() -> Optional[AccessInfo]:
    jwt_in_request = verify_jwt_in_request()
    if jwt_in_request is None:
        return None
    user_email = get_jwt_identity()
    if user_email is not None:
        permissions = get_user_permissions(user_email)
        return AccessInfo(
            user_email=user_email, access_type=AccessTypeEnum.JWT, permissions=permissions
        )
    return None



def get_access_info_from_jwt_or_api_key() -> AccessInfo:
    user_email_api_key = get_user_email_from_api_key()
    if user_email_api_key is not None:
        return AccessInfo(
            user_email=user_email_api_key, access_type=AccessTypeEnum.API_KEY
        )
    access_info = get_access_info_from_jwt()
    if access_info is not None:
        return access_info

    abort(code=HTTPStatus.UNAUTHORIZED, message=JWT_OR_API_KEY_NEEDED_ERROR_MESSAGE)


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


def permission_denied_abort() -> None:
    abort(code=HTTPStatus.FORBIDDEN, message="You do not have permission to access this endpoint")


def check_permissions_with_access_info(
        access_info: AccessInfo,
        permissions: list[PermissionsEnum]
) -> None:
    if access_info is None:
        return permission_denied_abort()
    for permission in permissions:
        if permission not in access_info.permissions:
            return permission_denied_abort()

def get_authentication_error_message(allowed_access_methods: list[AccessTypeEnum]) -> str:
    f"""
    Please provide a valid form of one of the following: {[access_method.value for access_method in allowed_access_methods]} 
    """

def get_authentication(
    allowed_access_methods: list[AccessTypeEnum],
    restrict_to_permissions: Optional[list[PermissionsEnum]] = None,
):
    # TODO: Test
    if AccessTypeEnum.API_KEY in allowed_access_methods:
        user_email_api_key = get_user_email_from_api_key()
        if user_email_api_key is not None:
            return AccessInfo(
                user_email=user_email_api_key, access_type=AccessTypeEnum.API_KEY
            )
    if AccessTypeEnum.JWT in allowed_access_methods:
        access_info = get_access_info_from_jwt()
        if restrict_to_permissions is not None:
            check_permissions_with_access_info(access_info, restrict_to_permissions)
        if access_info is not None:
            return access_info

    abort(code=HTTPStatus.UNAUTHORIZED, message=get_authentication_error_message(allowed_access_methods))
