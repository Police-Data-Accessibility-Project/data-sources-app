from middleware.schema_and_dto.dtos.reset_password.reset import ResetPasswordDTO
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    pydantic_to_marshmallow,
)

ResetPasswordSchema = pydantic_to_marshmallow(ResetPasswordDTO)
