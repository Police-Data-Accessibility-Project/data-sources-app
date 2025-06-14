from middleware.schema_and_dto.dtos.agencies.put import AgencyInfoPutDTO
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    generate_marshmallow_schema,
)

AgencyInfoPutSchema = generate_marshmallow_schema(AgencyInfoPutDTO)
