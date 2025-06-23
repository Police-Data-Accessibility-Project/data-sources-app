from typing import Optional

from flask_jwt_extended import decode_token
from jwt import ExpiredSignatureError
from werkzeug.exceptions import Forbidden, Unauthorized, BadRequest

from db.client.core import DatabaseClient
from middleware.enums import PermissionsEnum
from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.security.access_info.refresh import RefreshAccessInfo
from middleware.security.api_key.core import ApiKey
from middleware.security.jwt.core import SimpleJWT
from middleware.security.jwt.enums import JWTPurpose


def check_permissions_with_access_info(
    access_info: AccessInfoPrimary, permissions: list[PermissionsEnum]
) -> None:
    if access_info is None:
        raise Forbidden("You do not have permission to access this endpoint")
    if access_info.permissions is None:
        raise Forbidden("You do not have permission to access this endpoint")
    for permission in permissions:
        if permission not in access_info.permissions:
            raise Forbidden("You do not have permission to access this endpoint")


def get_user_email_from_api_key(token: str) -> Optional[str]:
    api_key = ApiKey(raw_key=token)
    db_client = DatabaseClient()
    user_identifiers = db_client.get_user_by_api_key(api_key.key_hash)
    if user_identifiers is None:
        return None
    return user_identifiers.email


def decode_jwt_with_purpose(token: str, purpose: JWTPurpose):
    try:
        return SimpleJWT.decode(token=token, expected_purpose=purpose)
    except ExpiredSignatureError:
        raise Unauthorized("Token is expired. Please request a new token.")


def validate_refresh_token(token: str, **kwargs) -> Optional[RefreshAccessInfo]:
    try:
        decode_token(token)
    except ExpiredSignatureError:
        raise Unauthorized("Refresh token has expired")

    decoded_refresh_token = decode_token(token)
    token_type: str = decoded_refresh_token["type"]
    # The below is flagged as a false positive through bandit security linting, misidentifying it as a password
    if token_type != "refresh":  # nosec
        raise BadRequest("Invalid refresh token")

    decoded_email = decoded_refresh_token["email"]
    return RefreshAccessInfo(user_email=decoded_email)
