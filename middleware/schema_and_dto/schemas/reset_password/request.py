from middleware.schema_and_dto.dynamic_logic.pydantic_to_marshmallow.core import (
    generate_marshmallow_schema,
)
from middleware.schema_and_dto.dtos.reset_password.request import (
    RequestResetPasswordRequestDTO,
)

RequestResetPasswordRequestSchema = generate_marshmallow_schema(
    RequestResetPasswordRequestDTO
)
