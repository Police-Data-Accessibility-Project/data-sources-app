from middleware.schema_and_dto.dtos.reset_password.request import (
    RequestResetPasswordRequestDTO,
)
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    generate_marshmallow_schema,
)

RequestResetPasswordRequestSchema = generate_marshmallow_schema(
    RequestResetPasswordRequestDTO
)
