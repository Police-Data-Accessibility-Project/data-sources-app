from endpoints.schema_config.config.core import EndpointSchemaConfig
from endpoints.instantiations.source_collector.data_sources.duplicates.dto import (
    SourceCollectorDuplicatesPostRequestDTO,
)
from endpoints.instantiations.source_collector.data_sources.duplicates.schemas.request import (
    SourceCollectorDuplicatesPostRequestSchema,
)
from endpoints.instantiations.source_collector.data_sources.duplicates.schemas.response import (
    SourceCollectorDuplicatePostResponseSchema,
)

SourceCollectorDuplicatesPostEndpointSchemaConfig = EndpointSchemaConfig(
    input_schema=SourceCollectorDuplicatesPostRequestSchema(),
    input_dto_class=SourceCollectorDuplicatesPostRequestDTO,
    primary_output_schema=SourceCollectorDuplicatePostResponseSchema(),
)
