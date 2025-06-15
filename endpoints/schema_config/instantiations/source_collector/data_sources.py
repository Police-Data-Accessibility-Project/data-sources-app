from endpoints.instantiations.source_collector.data_sources.post.schemas.request import (
    SourceCollectorPostRequestSchema,
)
from endpoints.instantiations.source_collector.data_sources.post.schemas.response import (
    SourceCollectorPostResponseSchema,
)
from endpoints.schema_config.config.core import EndpointSchemaConfig
from endpoints.instantiations.source_collector.data_sources.post.dtos.request import (
    SourceCollectorPostRequestDTO,
)

SourceCollectorDataSourcesPostEndpointSchemaConfig = EndpointSchemaConfig(
    input_schema=SourceCollectorPostRequestSchema(),
    input_dto_class=SourceCollectorPostRequestDTO,
    primary_output_schema=SourceCollectorPostResponseSchema(),
)
