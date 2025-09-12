from endpoints.instantiations.source_collector.agencies.search.locations.dtos.request import (
    SourceCollectorAgencySearchLocationRequestDTO,
)
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    pydantic_to_marshmallow,
)

SourceCollectorAgencySearchLocationRequestSchema = pydantic_to_marshmallow(
    SourceCollectorAgencySearchLocationRequestDTO
)
