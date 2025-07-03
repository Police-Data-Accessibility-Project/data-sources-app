from endpoints.instantiations.source_collector.sync.dtos.request import (
    SourceCollectorSyncAgenciesRequestDTO,
)
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    pydantic_to_marshmallow,
)

SourceCollectorSyncAgenciesRequestSchema = pydantic_to_marshmallow(
    SourceCollectorSyncAgenciesRequestDTO
)
