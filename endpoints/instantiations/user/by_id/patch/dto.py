from typing import Optional

from pydantic import BaseModel, field_validator

from db.enums import UserCapacityEnum
from middleware.schema_and_dto.dtos._helpers import (
    default_field_not_required,
)
from middleware.schema_and_dto.dtos.user.display_name import validate_display_name


class UserPatchDTO(BaseModel):
    capacities: Optional[list[UserCapacityEnum]] = default_field_not_required(
        description="The capacities of the user. Optional.",
    )
    display_name: Optional[str] = default_field_not_required(
        description=(
            "Public display name. Letters, numbers, hyphens, and underscores; "
            "3-30 characters; unique (case-insensitive)."
        ),
    )

    @field_validator("display_name")
    @classmethod
    def _validate_display_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return validate_display_name(value)
