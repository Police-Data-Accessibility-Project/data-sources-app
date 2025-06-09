from middleware.schema_and_dto_logic.dtos.reset_password.reset import ResetPasswordDTO
from middleware.schema_and_dto_logic.dynamic_logic.pydantic_to_marshmallow.core import (
    generate_marshmallow_schema,
)

ResetPasswordSchema = generate_marshmallow_schema(ResetPasswordDTO)
