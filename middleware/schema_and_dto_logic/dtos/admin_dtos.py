from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel, Field

from middleware.enums import PermissionsEnum
from middleware.schema_and_dto_logic.dtos.helpers import (
    default_field_required,
)


@dataclass
class AdminUserPostDTO:
    email: str
    password: str
    permissions: list[PermissionsEnum]


class AdminUserPutDTO(BaseModel):
    password: str = default_field_required(
        description="The new password of the admin user",
    )
