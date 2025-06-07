from marshmallow import Schema, fields

from middleware.schema_and_dto_logic.dynamic_logic.pydantic_to_marshmallow.core import (
    generate_marshmallow_schema,
)
from middleware.schema_and_dto_logic.dtos.request_reset_password_dtos import (
    RequestResetPasswordRequestDTO,
)
from middleware.schema_and_dto_logic.util import get_json_metadata


RequestResetPasswordRequestSchema = generate_marshmallow_schema(
    RequestResetPasswordRequestDTO
)
