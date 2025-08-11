from middleware.schema_and_dto.dtos.agencies.base import AgencyInfoBaseDTO
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    pydantic_to_marshmallow,
)

AgencyInfoBaseSchema = pydantic_to_marshmallow(AgencyInfoBaseDTO)
