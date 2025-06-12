from middleware.schema_and_dto.dtos.common.base import GetByIDBaseDTO
from middleware.schema_and_dto.dynamic_logic.pydantic_to_marshmallow.core import (
    generate_marshmallow_schema,
)

GetByIDBaseSchema = generate_marshmallow_schema(GetByIDBaseDTO)
