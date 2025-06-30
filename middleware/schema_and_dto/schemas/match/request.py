from middleware.schema_and_dto.dtos.match.request import AgencyMatchRequestDTO
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    pydantic_to_marshmallow,
)

AgencyMatchSchema = pydantic_to_marshmallow(AgencyMatchRequestDTO)
