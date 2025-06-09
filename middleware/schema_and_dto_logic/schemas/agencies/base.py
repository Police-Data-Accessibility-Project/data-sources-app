from middleware.schema_and_dto_logic.dtos.agencies.base import AgencyInfoBaseDTO
from middleware.schema_and_dto_logic.dynamic_logic.pydantic_to_marshmallow.core import (
    generate_marshmallow_schema,
)

AgencyInfoBaseSchema = generate_marshmallow_schema(AgencyInfoBaseDTO)
