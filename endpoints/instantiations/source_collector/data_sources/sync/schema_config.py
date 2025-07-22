from endpoints.instantiations.source_collector.data_sources.sync.dtos.request import (
    SourceCollectorSyncDataSourcesRequestDTO,
)
from endpoints.instantiations.source_collector.data_sources.sync.schemas.request import (
    SourceCollectorSyncDataSourcesRequestSchema,
)
from endpoints.instantiations.source_collector.data_sources.sync.schemas.response import (
    SourceCollectorSyncDataSourcesResponseSchema,
)
from endpoints.schema_config.config.core import EndpointSchemaConfig

SourceCollectorSyncDataSourceSchemaConfig = EndpointSchemaConfig(
    input_schema=SourceCollectorSyncDataSourcesRequestSchema,
    input_dto_class=SourceCollectorSyncDataSourcesRequestDTO,
    primary_output_schema=SourceCollectorSyncDataSourcesResponseSchema,
)
