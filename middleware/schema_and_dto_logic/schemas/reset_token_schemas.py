from marshmallow import Schema, fields

from middleware.schema_and_dto_logic.dynamic_logic.pydantic_to_marshmallow.core import (
    generate_marshmallow_schema,
)
from middleware.schema_and_dto_logic.dtos.reset_token_dtos import (
    RequestResetPasswordRequestDTO,
    ResetPasswordDTO,
)
from utilities.enums import SourceMappingEnum

ResetPasswordRequestSchema = generate_marshmallow_schema(RequestResetPasswordRequestDTO)

ResetPasswordSchema = generate_marshmallow_schema(ResetPasswordDTO)
