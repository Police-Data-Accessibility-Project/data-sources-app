from endpoints.instantiations.source_collector.sync.dtos.request import (
    SourceCollectorSyncAgenciesRequestDTO,
)
from endpoints.instantiations.source_collector.sync.schemas.request import (
    SourceCollectorSyncAgenciesRequestSchema,
)
from endpoints.instantiations.source_collector.sync.schemas.response import (
    SourceCollectorSyncAgenciesResponseSchema,
)
from endpoints.schema_config.config.core import EndpointSchemaConfig

SourceCollectorSyncAgenciesSchemaConfig = EndpointSchemaConfig(
    input_schema=SourceCollectorSyncAgenciesRequestSchema(),
    input_dto_class=SourceCollectorSyncAgenciesRequestDTO,
    primary_output_schema=SourceCollectorSyncAgenciesResponseSchema(),
)
