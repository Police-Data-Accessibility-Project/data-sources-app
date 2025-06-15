from endpoints.instantiations.source_collector.sync.dtos.request import (
    SourceCollectorSyncAgenciesRequestDTO,
)
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    generate_marshmallow_schema,
)

SourceCollectorSyncAgenciesRequestSchema = generate_marshmallow_schema(
    SourceCollectorSyncAgenciesRequestDTO
)
