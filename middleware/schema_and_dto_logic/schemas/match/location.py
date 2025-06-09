from middleware.schema_and_dto_logic.dtos.match.response import (
    AgencyMatchResponseLocationDTO,
)
from middleware.schema_and_dto_logic.dynamic_logic.pydantic_to_marshmallow.core import (
    generate_marshmallow_schema,
)

MatchAgenciesLocationSchema = generate_marshmallow_schema(
    AgencyMatchResponseLocationDTO
)
