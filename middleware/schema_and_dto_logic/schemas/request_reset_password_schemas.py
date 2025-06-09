from middleware.schema_and_dto_logic.dynamic_logic.pydantic_to_marshmallow.core import (
    generate_marshmallow_schema,
)
from middleware.schema_and_dto_logic.dtos.reset_password.request import (
    RequestResetPasswordRequestDTO,
)

RequestResetPasswordRequestSchema = generate_marshmallow_schema(
    RequestResetPasswordRequestDTO
)
