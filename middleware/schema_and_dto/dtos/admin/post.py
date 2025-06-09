from dataclasses import dataclass

from middleware.enums import PermissionsEnum


@dataclass
class AdminUserPostDTO:
    email: str
    password: str
    permissions: list[PermissionsEnum]
