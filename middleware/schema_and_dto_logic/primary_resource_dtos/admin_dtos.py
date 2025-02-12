from dataclasses import dataclass
from typing import Optional

from middleware.enums import PermissionsEnum


@dataclass
class AdminUserPostDTO:
    email: str
    password: str
    permissions: list[PermissionsEnum]


@dataclass
class AdminUserPutDTO:
    password: Optional[str] = None
