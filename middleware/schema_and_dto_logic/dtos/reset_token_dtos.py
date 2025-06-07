from pydantic import BaseModel

from middleware.schema_and_dto_logic.dtos.helpers import (
    default_field_required,
)


class RequestResetPasswordRequestDTO(BaseModel):
    email: str = default_field_required(description="The email of the user.")
    token: str = default_field_required(description="The token of the user.")


class ResetPasswordDTO(BaseModel):
    password: str = default_field_required(description="The new password of the user.")
