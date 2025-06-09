from middleware.schema_and_dto_logic.dtos.match.request import AgencyMatchRequestDTO
from middleware.schema_and_dto_logic.dynamic_logic.pydantic_to_marshmallow.core import (
    generate_marshmallow_schema,
)

AgencyMatchSchema = generate_marshmallow_schema(AgencyMatchRequestDTO)
