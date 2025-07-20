from endpoints.instantiations.source_collector.data_sources.sync.dtos.response import (
    SourceCollectorSyncDataSourcesResponseDTO,
)
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    pydantic_to_marshmallow,
)

SourceCollectorSyncDataSourcesResponseSchema = pydantic_to_marshmallow(
    SourceCollectorSyncDataSourcesResponseDTO
)
