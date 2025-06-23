from typing import Optional

from middleware.enums import AccessTypeEnum
from middleware.security.access_info.password_reset import PasswordResetTokenAccessInfo
from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.security.access_info.validate_email import ValidateEmailTokenAccessInfo
from middleware.security.auth.method_config.helpers import (
    check_permissions_with_access_info,
    get_user_email_from_api_key,
    decode_jwt_with_purpose,
)
from middleware.security.jwt.enums import JWTPurpose
from middleware.security.jwt.service import JWTService


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
    if isinstance(decoded_jwt.sub, str):
        raise ValueError("Sub is not a valid dictionary.")
    return PasswordResetTokenAccessInfo(
        user_id=int(decoded_jwt.sub["user_id"]),
        user_email=decoded_jwt.sub["user_email"],
        reset_token=decoded_jwt.sub["token"],
    )


def validate_email_handler(
    token: str, **kwargs
) -> Optional[ValidateEmailTokenAccessInfo]:
    decoded_jwt = decode_jwt_with_purpose(
        token=token, purpose=JWTPurpose.VALIDATE_EMAIL
    )
    if isinstance(decoded_jwt.sub, str):
        raise ValueError("Sub is not a valid dictionary.")
    return ValidateEmailTokenAccessInfo(
        validate_email_token=decoded_jwt.sub["token"],
    )
