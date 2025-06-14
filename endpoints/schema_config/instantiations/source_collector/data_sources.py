from endpoints.instantiations.source_collector.schemas.post.request import (
    SourceCollectorPostRequestSchema,
)
from endpoints.instantiations.source_collector.schemas.post.response import (
    SourceCollectorPostResponseSchema,
)
from endpoints.schema_config.config.core import EndpointSchemaConfig
from endpoints.instantiations.source_collector.dtos.data_sources.post.request import (
    SourceCollectorPostRequestDTO,
)

SourceCollectorDataSourcesPostEndpointSchemaConfig = EndpointSchemaConfig(
    input_schema=SourceCollectorPostRequestSchema(),
    input_dto_class=SourceCollectorPostRequestDTO,
    primary_output_schema=SourceCollectorPostResponseSchema(),
)
