from endpoints.instantiations.source_collector.sync.dtos.response import (
    SourceCollectorSyncAgenciesResponseOuterDTO,
)
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    generate_marshmallow_schema,
)

SourceCollectorSyncAgenciesResponseSchema = generate_marshmallow_schema(
    SourceCollectorSyncAgenciesResponseOuterDTO
)
