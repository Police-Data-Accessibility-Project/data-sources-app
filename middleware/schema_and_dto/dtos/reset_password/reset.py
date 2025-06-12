from pydantic import BaseModel

from middleware.schema_and_dto.dtos._helpers import default_field_required


class ResetPasswordDTO(BaseModel):
    password: str = default_field_required(description="The new password of the user.")
