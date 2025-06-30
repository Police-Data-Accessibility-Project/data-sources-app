from middleware.schema_and_dto.dtos.match.response import (
    AgencyMatchResponseLocationDTO,
)
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    pydantic_to_marshmallow,
)

MatchAgenciesLocationSchema = pydantic_to_marshmallow(AgencyMatchResponseLocationDTO)
