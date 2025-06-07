from middleware.schema_and_dto_logic.dtos.agencies_dtos import AgencyInfoPostDTO
from middleware.schema_and_dto_logic.dynamic_logic.pydantic_to_marshmallow.core import (
    generate_marshmallow_schema,
)

AgencyInfoPostSchema = generate_marshmallow_schema(AgencyInfoPostDTO)
