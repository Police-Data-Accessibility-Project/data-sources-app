from endpoints.instantiations.source_collector.meta_urls.post.dtos.request import (
    SourceCollectorMetaURLPostRequestDTO,
)
from endpoints.instantiations.source_collector.meta_urls.post.schemas.request import (
    SourceCollectorMetaURLPostRequestSchema,
)
from endpoints.instantiations.source_collector.meta_urls.post.schemas.response import (
    SourceCollectorMetaURLPostResponseSchema,
)
from endpoints.schema_config.config.core import EndpointSchemaConfig

SourceCollectorMetaURLPostEndpointSchemaConfig = EndpointSchemaConfig(
    input_schema=SourceCollectorMetaURLPostRequestSchema(),
    input_dto_class=SourceCollectorMetaURLPostRequestDTO,
    primary_output_schema=SourceCollectorMetaURLPostResponseSchema(),
)
