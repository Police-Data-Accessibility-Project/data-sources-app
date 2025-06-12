from middleware.enums import PermissionsEnum, AccessTypeEnum
from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.security.jwt.enums import JWTPurpose
from middleware.util.env import get_env_variable


def get_secret_key(purpose: JWTPurpose):
    if purpose == JWTPurpose.PASSWORD_RESET:
        return get_env_variable("RESET_PASSWORD_SECRET_KEY")
    elif purpose == JWTPurpose.GITHUB_ACCESS_TOKEN:
        return get_env_variable("JWT_SECRET_KEY")
    elif purpose == JWTPurpose.VALIDATE_EMAIL:
        return get_env_variable("VALIDATE_EMAIL_SECRET_KEY")
    elif purpose == JWTPurpose.STANDARD_ACCESS_TOKEN:
        return get_env_variable("JWT_SECRET_KEY")
    else:
        raise Exception(f"Invalid JWT Purpose: {purpose}")


def get_jwt_access_info_with_permissions(
    user_email, user_id, permissions_raw_str: list[str]
):
    permissions = []
    for permission_raw_str in permissions_raw_str:
        permission = PermissionsEnum(permission_raw_str)
        permissions.append(permission)
    return AccessInfoPrimary(
        user_email=user_email,
        user_id=user_id,
        access_type=AccessTypeEnum.JWT,
        permissions=permissions,
    )
