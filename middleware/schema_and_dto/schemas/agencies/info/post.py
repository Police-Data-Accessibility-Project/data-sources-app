from middleware.schema_and_dto.dtos.agencies.post import AgencyInfoPostDTO
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    generate_marshmallow_schema,
)

AgencyInfoPostSchema = generate_marshmallow_schema(AgencyInfoPostDTO)
