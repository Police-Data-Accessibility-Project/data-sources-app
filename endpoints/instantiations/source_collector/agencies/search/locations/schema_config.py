from endpoints.instantiations.source_collector.agencies.search.locations.dtos.request import \
    SourceCollectorAgencySearchLocationRequestDTO
from endpoints.instantiations.source_collector.agencies.search.locations.schemas.request import \
    SourceCollectorAgencySearchLocationRequestSchema
from endpoints.instantiations.source_collector.agencies.search.locations.schemas.response import \
    SourceCollectorAgencySearchLocationResponseSchema
from endpoints.schema_config.config.core import EndpointSchemaConfig

SourceCollectorAgencySearchLocationSchemaConfig = EndpointSchemaConfig(
    input_schema=SourceCollectorAgencySearchLocationRequestSchema,
    input_dto_class=SourceCollectorAgencySearchLocationRequestDTO,
    primary_output_schema=SourceCollectorAgencySearchLocationResponseSchema,
)
