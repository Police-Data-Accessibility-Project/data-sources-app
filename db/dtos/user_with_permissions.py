from db.dtos.user_info_non_sensitive import UserInfoNonSensitive
from middleware.enums import PermissionsEnum


class UsersWithPermissions(UserInfoNonSensitive):
    permissions: list[PermissionsEnum]
