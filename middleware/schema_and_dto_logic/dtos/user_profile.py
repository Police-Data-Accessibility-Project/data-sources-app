from pydantic import BaseModel

from middleware.schema_and_dto_logic.dtos._helpers import (
    default_field_required,
)


class UserPutDTO(BaseModel):
    old_password: str = default_field_required(
        description="The old password of the user."
    )
    new_password: str = default_field_required(
        description="The new password of the user."
    )
