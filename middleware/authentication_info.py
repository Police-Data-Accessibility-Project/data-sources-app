from typing import Optional

from pydantic import BaseModel

from middleware.enums import AccessTypeEnum, PermissionsEnum


class AuthenticationInfo(BaseModel):
    """
    A dataclass providing information on how the user was authenticated
    """

    allowed_access_methods: Optional[list[AccessTypeEnum]] = None
    no_auth: bool = False
    restrict_to_permissions: Optional[list[PermissionsEnum]] = None

    def requires_admin_permissions(self) -> bool:
        if self.restrict_to_permissions is None:
            return False
        return len(self.restrict_to_permissions) > 0


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
