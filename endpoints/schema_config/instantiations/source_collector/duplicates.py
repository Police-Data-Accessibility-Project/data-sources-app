from endpoints.schema_config.config.core import EndpointSchemaConfig
from endpoints.instantiations.source_collector.dtos.data_sources.duplicates import (
    SourceCollectorDuplicatesPostRequestDTO,
)
from endpoints.instantiations.source_collector.schemas.duplicate.request import (
    SourceCollectorDuplicatesPostRequestSchema,
)
from endpoints.instantiations.source_collector.schemas.duplicate.response import (
    SourceCollectorDuplicatePostResponseSchema,
)

SourceCollectorDuplicatesPostEndpointSchemaConfig = EndpointSchemaConfig(
    input_schema=SourceCollectorDuplicatesPostRequestSchema(),
    input_dto_class=SourceCollectorDuplicatesPostRequestDTO,
    primary_output_schema=SourceCollectorDuplicatePostResponseSchema(),
)
