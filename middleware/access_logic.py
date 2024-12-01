from collections import namedtuple
from enum import Enum
from http import HTTPStatus
from typing import Optional

from flask import request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from flask_jwt_extended.exceptions import NoAuthorizationError
from flask_restx import abort
from jwt import ExpiredSignatureError
from pydantic import BaseModel
from typing_extensions import Callable

from database_client.database_client import DatabaseClient
from middleware.SimpleJWT import SimpleJWT, JWTPurpose
from middleware.api_key import ApiKey
from middleware.enums import PermissionsEnum, AccessTypeEnum
from database_client.helper_functions import get_db_client
from middleware.exceptions import (
    InvalidAPIKeyException,
)
from middleware.flask_response_manager import FlaskResponseManager
from middleware.primary_resource_logic.permissions_logic import get_user_permissions


class AuthenticationInfo(BaseModel):
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
RESET_PASSWORD_AUTH_INFO = AuthenticationInfo(
    allowed_access_methods=[AccessTypeEnum.RESET_PASSWORD]
)
VALIDATE_EMAIL_AUTH_INFO = AuthenticationInfo(
    allowed_access_methods=[AccessTypeEnum.VALIDATE_EMAIL],
)


class AuthScheme(Enum):
    BEARER = "Bearer"
    BASIC = "Basic"


class HeaderAuthInfo(BaseModel):
    auth_scheme: AuthScheme
    token: str


def get_header_auth_info() -> HeaderAuthInfo:
    authorization_header = get_authorization_header_from_request()
    try:
        authorization_header_parts = authorization_header.split(" ")
        if len(authorization_header_parts) != 2:
            bad_request_abort()
        scheme_string = AuthScheme(authorization_header_parts[0])
        token = authorization_header_parts[1]
        return HeaderAuthInfo(auth_scheme=AuthScheme(scheme_string), token=token)
    except (ValueError, IndexError, AttributeError):
        bad_request_abort(message="Improperly formatted authorization header")


class ParserDeterminator:
    """
    Determines proper parser to use
    """

    def __init__(self, allowed_access_methods: list[AccessTypeEnum]):
        self.allowed_access_methods = allowed_access_methods

    def is_access_type_allowed(self, access_type: AccessTypeEnum) -> bool:
        return access_type in self.allowed_access_methods


class AccessInfoBase(BaseModel):
    access_type: AccessTypeEnum


class AccessInfoPrimary(AccessInfoBase):
    """
    A dataclass providing information on how the endpoint was accessed
    """

    user_email: str
    user_id: Optional[int] = None
    permissions: list[PermissionsEnum] = None

    def get_user_id(self) -> Optional[int]:
        if self.user_id is None:
            self.user_id = DatabaseClient().get_user_id(email=self.user_email)
        return self.user_id


class PasswordResetTokenAccessInfo(AccessInfoBase):
    access_type: AccessTypeEnum = AccessTypeEnum.RESET_PASSWORD
    user_id: int
    user_email: str
    reset_token: str


class ValidateEmailTokenAccessInfo(AccessInfoBase):
    access_type: AccessTypeEnum = AccessTypeEnum.VALIDATE_EMAIL
    validate_email_token: str


class JWTService:
    @staticmethod
    def get_identity():
        try:
            verify_jwt_in_request()
            return get_jwt_identity()
        except NoAuthorizationError:
            FlaskResponseManager.abort(
                HTTPStatus.BAD_REQUEST, message="Token is missing"
            )
        except Exception as e:
            return None

    @staticmethod
    def get_access_info(token: str):
        simple_jwt = SimpleJWT.decode(token, purpose=JWTPurpose.STANDARD_ACCESS_TOKEN)
        identity = JWTService.get_identity()
        if identity:
            return get_jwt_access_info_with_permissions(
                user_email=identity["user_email"], user_id=identity["id"]
            )
        return None


def get_token_from_request_header(scheme: AuthScheme):
    authorization_header = get_authorization_header_from_request()
    return get_key_from_authorization_header(authorization_header, scheme=scheme.value)


def get_key_from_authorization_header(
    authorization_header: str, scheme: str = "Basic"
) -> str:
    try:
        authorization_header_parts = authorization_header.split(" ")
        if len(authorization_header_parts) != 2:
            bad_request_abort()
        if authorization_header_parts[0] != scheme:
            raise InvalidAPIKeyException
        return authorization_header_parts[1]
    except (ValueError, IndexError, AttributeError):
        raise InvalidAPIKeyException


def decode_jwt_with_purpose(token: str, purpose: JWTPurpose):
    try:
        return SimpleJWT.decode(token=token, purpose=purpose)
    except ExpiredSignatureError:
        abort(
            code=HTTPStatus.UNAUTHORIZED,
            message="Token is expired. Please request a new token.",
        )


def get_jwt_access_info_with_permissions(user_email, user_id):
    permissions = get_user_permissions(user_email)
    return AccessInfoPrimary(
        user_email=user_email,
        user_id=user_id,
        access_type=AccessTypeEnum.JWT,
        permissions=permissions,
    )


def get_user_email_from_api_key(token: str) -> Optional[str]:
    api_key = ApiKey(raw_key=token)
    db_client = get_db_client()
    user_identifiers = db_client.get_user_by_api_key(api_key.key_hash)
    return user_identifiers.email


def get_authorization_header_from_request() -> str:
    headers = request.headers
    try:
        return headers["Authorization"]
    except (KeyError, TypeError):
        FlaskResponseManager.abort(
            code=HTTPStatus.BAD_REQUEST, message="Authorization header missing"
        )


def bad_request_abort(
    message: str = "Improperly formatted authorization header",
):
    return FlaskResponseManager.abort(code=HTTPStatus.BAD_REQUEST, message=message)


def permission_denied_abort() -> None:
    abort(
        code=HTTPStatus.FORBIDDEN,
        message="You do not have permission to access this endpoint",
    )


def check_permissions_with_access_info(
    access_info: AccessInfoPrimary, permissions: list[PermissionsEnum]
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


def try_authentication(
    allowed_access_methods: list[AccessTypeEnum],
    access_type: AccessTypeEnum,
    handler: callable,
    **kwargs,
):
    """
    Generalized function to attempt authentication using a specific handler.

    :param allowed_access_methods: List of allowed access methods.
    :param access_type: The type of access being authenticated (e.g., JWT, API_KEY).
    :param handler: A callable that handles the specific authentication logic.
    :return: AccessInfo or None if authentication fails.
    """
    if access_type in allowed_access_methods:
        return handler(**kwargs)
    return None


def jwt_handler(
    token: str, restrict_to_permissions=None
) -> Optional[AccessInfoPrimary]:
    access_info = JWTService.get_access_info(token=token)
    if not access_info:
        return None
    if restrict_to_permissions:
        check_permissions_with_access_info(access_info, restrict_to_permissions)
    return access_info


def api_key_handler(token: str, **kwargs) -> Optional[AccessInfoPrimary]:
    user_email = get_user_email_from_api_key(token)
    if user_email:
        return AccessInfoPrimary(
            user_email=user_email,
            access_type=AccessTypeEnum.API_KEY,
        )
    return None


def password_reset_handler(
    token: str, **kwargs
) -> Optional[PasswordResetTokenAccessInfo]:
    decoded_jwt = decode_jwt_with_purpose(
        token=token, purpose=JWTPurpose.PASSWORD_RESET
    )
    return PasswordResetTokenAccessInfo(
        user_id=decoded_jwt.sub["user_id"],
        user_email=decoded_jwt.sub["user_email"],
        reset_token=decoded_jwt.sub["token"],
    )


def validate_email_handler(
    token: str, **kwargs
) -> Optional[ValidateEmailTokenAccessInfo]:
    decoded_jwt = decode_jwt_with_purpose(
        token=token, purpose=JWTPurpose.VALIDATE_EMAIL
    )
    return ValidateEmailTokenAccessInfo(
        validate_email_token=decoded_jwt.sub["token"],
    )


class AuthMethodConfig(BaseModel):
    handler: Callable
    scheme: AuthScheme


AUTH_METHODS_MAP = {
    AccessTypeEnum.JWT: AuthMethodConfig(handler=jwt_handler, scheme=AuthScheme.BEARER),
    AccessTypeEnum.API_KEY: AuthMethodConfig(
        handler=api_key_handler, scheme=AuthScheme.BASIC
    ),
    AccessTypeEnum.RESET_PASSWORD: AuthMethodConfig(
        handler=password_reset_handler, scheme=AuthScheme.BEARER
    ),
    AccessTypeEnum.VALIDATE_EMAIL: AuthMethodConfig(
        handler=validate_email_handler, scheme=AuthScheme.BEARER
    ),
}


def get_authentication(
    allowed_access_methods: list[AccessTypeEnum],
    restrict_to_permissions: Optional[list[PermissionsEnum]] = None,
    no_auth: bool = False,
) -> Optional[AccessInfoPrimary]:
    """
    Authenticate the user based on allowed access methods and optionally restrict permissions.

    :param allowed_access_methods: List of allowed access methods (API_KEY, JWT).
    :param restrict_to_permissions: Optional list of permissions to restrict the access.
    :return: AccessInfo object containing user email and access type.
    :raises HTTPException: If authentication fails.
    """
    if no_auth:
        return None

    hai = get_header_auth_info()

    invalid_auth_scheme = False
    for access_method in allowed_access_methods:
        amc: AuthMethodConfig = AUTH_METHODS_MAP.get(access_method)
        if amc is None:
            continue

        if hai.auth_scheme != amc.scheme:
            invalid_auth_scheme = True
            continue

        access_info = try_authentication(
            allowed_access_methods=allowed_access_methods,
            access_type=access_method,
            handler=amc.handler,
            token=hai.token,
            restrict_to_permissions=restrict_to_permissions,
        )
        if access_info:
            return access_info

    if invalid_auth_scheme:
        bad_request_abort("Invalid Auth Scheme for endpoint")
    abort(
        code=HTTPStatus.UNAUTHORIZED,
        message=get_authentication_error_message(allowed_access_methods),
    )
