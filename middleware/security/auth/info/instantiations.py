from middleware.enums import AccessTypeEnum, PermissionsEnum
from middleware.security.auth.info.base import AuthenticationInfo

WRITE_ONLY_AUTH_INFO = AuthenticationInfo(
    allowed_access_methods=[AccessTypeEnum.JWT],
    restrict_to_permissions=[PermissionsEnum.DB_WRITE],
)
ARCHIVE_WRITE_AUTH_INFO = AuthenticationInfo(
    allowed_access_methods=[AccessTypeEnum.JWT],
    restrict_to_permissions=[PermissionsEnum.ARCHIVE_WRITE],
)
STANDARD_JWT_AUTH_INFO = AuthenticationInfo(
    allowed_access_methods=[AccessTypeEnum.JWT],
)
API_OR_JWT_AUTH_INFO = AuthenticationInfo(
    allowed_access_methods=[AccessTypeEnum.API_KEY, AccessTypeEnum.JWT],
)
NO_AUTH_INFO = AuthenticationInfo(no_auth=True)
RESET_PASSWORD_AUTH_INFO = AuthenticationInfo(
    allowed_access_methods=[AccessTypeEnum.RESET_PASSWORD]
)
VALIDATE_EMAIL_AUTH_INFO = AuthenticationInfo(
    allowed_access_methods=[AccessTypeEnum.VALIDATE_EMAIL],
)
READ_USER_AUTH_INFO = AuthenticationInfo(
    allowed_access_methods=[AccessTypeEnum.JWT],
    restrict_to_permissions=[PermissionsEnum.READ_ALL_USER_INFO],
)
WRITE_USER_AUTH_INFO = AuthenticationInfo(
    allowed_access_methods=[AccessTypeEnum.JWT],
    restrict_to_permissions=[PermissionsEnum.USER_CREATE_UPDATE],
)
