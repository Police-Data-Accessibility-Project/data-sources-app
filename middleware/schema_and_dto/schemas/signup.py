from middleware.schema_and_dto.dtos.signup import EmailOnlyDTO
from middleware.schema_and_dto.dynamic_logic.pydantic_to_marshmallow.core import (
    generate_marshmallow_schema,
)

EmailOnlySchema = generate_marshmallow_schema(EmailOnlyDTO)
