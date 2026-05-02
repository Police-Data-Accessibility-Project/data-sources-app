from typing import Optional

from pydantic import BaseModel, field_validator

from db.enums import UserCapacityEnum
from middleware.schema_and_dto.dtos._helpers import (
    default_field_required,
    default_field_not_required,
)
from middleware.schema_and_dto.dtos.user.display_name import validate_display_name


class UserStandardSignupRequestDTO(BaseModel):
    email: str = default_field_required(description="The email of the user")
    password: str = default_field_required(description="The password of the user")
    capacities: Optional[list[UserCapacityEnum]] = default_field_not_required(
        description="The capacities of the user"
    )
    display_name: Optional[str] = default_field_not_required(
        description=(
            "Public display name. Letters, numbers, hyphens, and underscores; "
            "3-30 characters; unique (case-insensitive). Defaults to the "
            "user's numeric id if omitted."
        )
    )

    @field_validator("display_name")
    @classmethod
    def _validate_display_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return validate_display_name(value)
