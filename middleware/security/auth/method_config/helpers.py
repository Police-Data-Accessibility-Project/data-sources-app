from http import HTTPStatus
from typing import Optional

from flask_jwt_extended import decode_token
from flask_restx import abort
from jwt import ExpiredSignatureError

from db.helper_functions import get_db_client
from middleware.enums import PermissionsEnum
from middleware.flask_response_manager import FlaskResponseManager
from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.security.access_info.refresh import RefreshAccessInfo
from middleware.security.api_key.core import ApiKey
from middleware.security.jwt.core import SimpleJWT
from middleware.security.jwt.enums import JWTPurpose


def check_permissions_with_access_info(
    access_info: AccessInfoPrimary, permissions: list[PermissionsEnum]
) -> None:
    if access_info is None:
        return FlaskResponseManager.permission_denied_abort()
    for permission in permissions:
        if permission not in access_info.permissions:
            return FlaskResponseManager.permission_denied_abort()


def get_user_email_from_api_key(token: str) -> Optional[str]:
    api_key = ApiKey(raw_key=token)
    db_client = get_db_client()
    user_identifiers = db_client.get_user_by_api_key(api_key.key_hash)
    if user_identifiers is None:
        return None
    return user_identifiers.email


def decode_jwt_with_purpose(token: str, purpose: JWTPurpose):
    try:
        return SimpleJWT.decode(token=token, expected_purpose=purpose)
    except ExpiredSignatureError:
        abort(
            code=HTTPStatus.UNAUTHORIZED,
            message="Token is expired. Please request a new token.",
        )


def validate_refresh_token(token: str, **kwargs) -> Optional[RefreshAccessInfo]:
    try:
        decode_token(token)
    except ExpiredSignatureError:
        FlaskResponseManager.abort(
            code=HTTPStatus.UNAUTHORIZED, message="Refresh token has expired"
        )
    decoded_refresh_token = decode_token(token)
    token_type: str = decoded_refresh_token["type"]
    # The below is flagged as a false positive through bandit security linting, misidentifying it as a password
    if token_type != "refresh":  # nosec
        FlaskResponseManager.abort(
            code=HTTPStatus.BAD_REQUEST, message="Invalid refresh token"
        )
    decoded_email = decoded_refresh_token["email"]
    return RefreshAccessInfo(user_email=decoded_email)
