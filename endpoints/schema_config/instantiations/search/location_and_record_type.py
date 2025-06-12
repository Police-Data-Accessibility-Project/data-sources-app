from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.dtos.search.request import SearchRequestsDTO
from middleware.schema_and_dto.schemas.search.request import SearchRequestSchema
from middleware.schema_and_dto.schemas.search.response.response import (
    SearchResponseSchema,
)

SearchLocationAndRecordTypeGetEndpointSchemaConfig = EndpointSchemaConfig(
    input_schema=SearchRequestSchema(),
    primary_output_schema=SearchResponseSchema(),
    input_dto_class=SearchRequestsDTO,
)
