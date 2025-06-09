from middleware.schema_and_dto.dtos.match.request import AgencyMatchRequestDTO
from middleware.schema_and_dto.dynamic_logic.pydantic_to_marshmallow.core import (
    generate_marshmallow_schema,
)

AgencyMatchSchema = generate_marshmallow_schema(AgencyMatchRequestDTO)
