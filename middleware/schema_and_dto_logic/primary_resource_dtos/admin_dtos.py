from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel, Field

from middleware.enums import PermissionsEnum


@dataclass
class AdminUserPostDTO:
    email: str
    password: str
    permissions: list[PermissionsEnum]


class AdminUserPutDTO(BaseModel):
    password: str = Field(
        description="The new password of the admin user",
    )
