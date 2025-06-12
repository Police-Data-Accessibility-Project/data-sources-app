from middleware.schema_and_dto.dtos.match.response import (
    AgencyMatchResponseLocationDTO,
)
from middleware.schema_and_dto.dynamic_logic.pydantic_to_marshmallow.core import (
    generate_marshmallow_schema,
)

MatchAgenciesLocationSchema = generate_marshmallow_schema(
    AgencyMatchResponseLocationDTO
)
