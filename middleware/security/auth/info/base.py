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
