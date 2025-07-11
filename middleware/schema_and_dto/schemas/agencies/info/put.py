from middleware.schema_and_dto.dtos.agencies.put import AgencyInfoPutDTO
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    pydantic_to_marshmallow,
)

AgencyInfoPutSchema = pydantic_to_marshmallow(AgencyInfoPutDTO)
