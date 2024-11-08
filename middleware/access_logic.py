from dataclasses import dataclass
from http import HTTPStatus
from typing import Optional

from flask import request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from flask_restx import abort

from middleware.api_key import ApiKey
from middleware.enums import PermissionsEnum, AccessTypeEnum
from database_client.helper_functions import get_db_client
from middleware.exceptions import (
    InvalidAPIKeyException,
    InvalidAuthorizationHeaderException,
)
from middleware.primary_resource_logic.permissions_logic import get_user_permissions

JWT_OR_API_KEY_NEEDED_ERROR_MESSAGE = "Please provide an API key with the format 'Basic <api_key>' OR an access token with the format 'Bearer <access_token>' in the request header in the 'Authorization' key "


@dataclass
class AuthenticationInfo:
    """
    A dataclass providing information on how the user was authenticated
    """

    allowed_access_methods: Optional[list[AccessTypeEnum]] = None
    no_auth: bool = False
    restrict_to_permissions: Optional[list[PermissionsEnum]] = None


WRITE_ONLY_AUTH_INFO = AuthenticationInfo(
    allowed_access_methods=[AccessTypeEnum.JWT],
    restrict_to_permissions=[PermissionsEnum.DB_WRITE],
)
# Allow owners of a resource to use the endpoint as well, instead of only admin-level users
STANDARD_JWT_AUTH_INFO = AuthenticationInfo(
    allowed_access_methods=[AccessTypeEnum.JWT],
)
GET_AUTH_INFO = AuthenticationInfo(
    allowed_access_methods=[AccessTypeEnum.API_KEY, AccessTypeEnum.JWT],
)
NO_AUTH_INFO = AuthenticationInfo(no_auth=True)


@dataclass
class AccessInfo:
    """
    A dataclass providing information on how the endpoint was accessed
    """

    user_email: str
    access_type: AccessTypeEnum
    permissions: list[PermissionsEnum] = None

    def get_user_id(self) -> Optional[int]:
        db_client = get_db_client()
        return db_client.get_user_id(self.user_email)


def get_access_info_from_jwt() -> Optional[AccessInfo]:
    jwt_in_request = verify_jwt_in_request()
    if jwt_in_request is None:
        return None
    identity = get_jwt_identity()
    if identity is None:
        return None
    return get_jwt_access_info_with_permissions(identity["user_email"])


def get_jwt_access_info_with_permissions(user_email):
    permissions = get_user_permissions(user_email)
    return AccessInfo(
        user_email=user_email, access_type=AccessTypeEnum.JWT, permissions=permissions
    )


def get_user_email_from_api_key() -> Optional[str]:
    try:
        raw_key = get_api_key_from_request_header()
    except (InvalidAPIKeyException, InvalidAuthorizationHeaderException):
        return None

    api_key = ApiKey(raw_key=raw_key)
    db_client = get_db_client()
    user_identifiers = db_client.get_user_by_api_key(api_key.key_hash)
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
    abort(
        code=HTTPStatus.FORBIDDEN,
        message="You do not have permission to access this endpoint",
    )


def check_permissions_with_access_info(
    access_info: AccessInfo, permissions: list[PermissionsEnum]
) -> None:
    if access_info is None:
        return permission_denied_abort()
    for permission in permissions:
        if permission not in access_info.permissions:
            return permission_denied_abort()


def get_authentication_error_message(
    allowed_access_methods: list[AccessTypeEnum],
) -> str:
    f"""
    Please provide a valid form of one of the following: {[access_method.value for access_method in allowed_access_methods]} 
    """


def get_authentication(
    allowed_access_methods: list[AccessTypeEnum],
    restrict_to_permissions: Optional[list[PermissionsEnum]] = None,
    no_auth: bool = False,
) -> Optional[AccessInfo]:
    """
    Authenticate the user based on allowed access methods and optionally restrict permissions.

    :param allowed_access_methods: List of allowed access methods (API_KEY, JWT).
    :param restrict_to_permissions: Optional list of permissions to restrict the access.
    :return: AccessInfo object containing user email and access type.
    :raises HTTPException: If authentication fails.
    """
    if no_auth:
        return None

    # Try to authenticate using API key if allowed
    access_info = try_api_key_authentication(allowed_access_methods)
    if access_info:
        return access_info

    # Try to authenticate using JWT if allowed
    access_info = try_jwt_authentication(
        allowed_access_methods, restrict_to_permissions
    )
    if access_info:
        return access_info

    # If neither method succeeds, abort with an unauthorized error
    abort(
        HTTPStatus.UNAUTHORIZED,
        message=get_authentication_error_message(allowed_access_methods),
    )


def try_api_key_authentication(
    allowed_access_methods: list[AccessTypeEnum],
) -> Optional[AccessInfo]:
    """Helper function to attempt API key authentication."""
    if AccessTypeEnum.API_KEY in allowed_access_methods:
        user_email = get_user_email_from_api_key()
        if user_email:
            return AccessInfo(user_email=user_email, access_type=AccessTypeEnum.API_KEY)
    return None


def try_jwt_authentication(
    allowed_access_methods: list[AccessTypeEnum],
    restrict_to_permissions: Optional[list[PermissionsEnum]] = None,
) -> Optional[AccessInfo]:
    """Helper function to attempt JWT authentication and check permissions."""
    if AccessTypeEnum.JWT not in allowed_access_methods:
        return None
    access_info = get_access_info_from_jwt()
    if not access_info:
        return None
    if restrict_to_permissions:
        check_permissions_with_access_info(access_info, restrict_to_permissions)
    return access_info
