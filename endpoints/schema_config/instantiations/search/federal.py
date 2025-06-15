from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.dtos.search.federal import FederalSearchRequestDTO
from middleware.schema_and_dto.schemas.search.federal.request import (
    FederalSearchRequestSchema,
)
from middleware.schema_and_dto.schemas.search.federal.response import (
    FederalSearchResponseSchema,
)

SearchFederalGetEndpointSchemaConfig = EndpointSchemaConfig(
    input_schema=FederalSearchRequestSchema(),
    primary_output_schema=FederalSearchResponseSchema(),
    input_dto_class=FederalSearchRequestDTO,
)
