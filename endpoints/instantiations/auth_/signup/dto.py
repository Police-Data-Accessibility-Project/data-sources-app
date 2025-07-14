from typing import Optional

from pydantic import BaseModel

from db.enums import UserCapacityEnum
from middleware.schema_and_dto.dtos._helpers import (
    default_field_required,
    default_field_not_required,
)


class UserStandardSignupRequestDTO(BaseModel):
    email: str = default_field_required(description="The email of the user")
    password: str = default_field_required(description="The password of the user")
    capacities: Optional[list[UserCapacityEnum]] = default_field_not_required(
        description="The capacities of the user"
    )
