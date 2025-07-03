from middleware.schema_and_dto.dtos.reset_password.request import (
    RequestResetPasswordRequestDTO,
)
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    pydantic_to_marshmallow,
)

RequestResetPasswordRequestSchema = pydantic_to_marshmallow(
    RequestResetPasswordRequestDTO
)
