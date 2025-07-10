from pydantic import BaseModel

from db.enums import UserCapacityEnum
from middleware.schema_and_dto.dtos._helpers import default_field_required


class UserPatchDTO(BaseModel):
    capacities: list[UserCapacityEnum] = default_field_required(
        description="The capacities of the user",
    )