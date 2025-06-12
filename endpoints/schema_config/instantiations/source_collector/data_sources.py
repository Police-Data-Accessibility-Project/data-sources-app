from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.dtos.source_collector.post.request import (
    SourceCollectorPostRequestDTO,
)
from middleware.schema_and_dto.schemas.source_collector.post.request import (
    SourceCollectorPostRequestSchema,
)
from middleware.schema_and_dto.schemas.source_collector.post.response import (
    SourceCollectorPostResponseSchema,
)

SourceCollectorDataSourcesPostEndpointSchemaConfig = EndpointSchemaConfig(
    input_schema=SourceCollectorPostRequestSchema(),
    input_dto_class=SourceCollectorPostRequestDTO,
    primary_output_schema=SourceCollectorPostResponseSchema(),
)
