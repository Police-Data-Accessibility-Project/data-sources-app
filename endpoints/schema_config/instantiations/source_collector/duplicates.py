from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.dtos.source_collector.data_sources.duplicates import (
    SourceCollectorDuplicatesPostRequestDTO,
)
from middleware.schema_and_dto.schemas.source_collector.duplicate.request import (
    SourceCollectorDuplicatesPostRequestSchema,
)
from middleware.schema_and_dto.schemas.source_collector.duplicate.response import (
    SourceCollectorDuplicatePostResponseSchema,
)

SourceCollectorDuplicatesPostEndpointSchemaConfig = EndpointSchemaConfig(
    input_schema=SourceCollectorDuplicatesPostRequestSchema(),
    input_dto_class=SourceCollectorDuplicatesPostRequestDTO,
    primary_output_schema=SourceCollectorDuplicatePostResponseSchema(),
)
