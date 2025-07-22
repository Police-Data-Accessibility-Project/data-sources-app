from endpoints.instantiations.source_collector.data_sources.sync.dtos.request import (
    SourceCollectorSyncDataSourcesRequestDTO,
)
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    pydantic_to_marshmallow,
)

SourceCollectorSyncDataSourcesRequestSchema = pydantic_to_marshmallow(
    SourceCollectorSyncDataSourcesRequestDTO
)
