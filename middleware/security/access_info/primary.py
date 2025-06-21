from typing import Optional

from db.client.core import DatabaseClient
from middleware.enums import PermissionsEnum
from middleware.security.access_info.base import AccessInfoBase


class AccessInfoPrimary(AccessInfoBase):
    """
    A dataclass providing information on how the endpoint was accessed
    """

    user_email: str
    user_id: Optional[int] = None
    permissions: Optional[list[PermissionsEnum]] = None

    def get_user_id(self) -> Optional[int]:
        if self.user_id is None:
            self.user_id = DatabaseClient().get_user_id(email=self.user_email)
        return self.user_id

    def has_permission(self, permission: PermissionsEnum) -> bool:
        if self.permissions is None:
            return False
        return permission in self.permissions
