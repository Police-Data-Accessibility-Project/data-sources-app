from endpoints.instantiations.search.core.models.request import SearchRequestDTO
from endpoints.instantiations.search.core.schemas.response import SearchResponseSchema
from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.schemas.search.request import SearchRequestSchema

SearchGetEndpointSchemaConfig = EndpointSchemaConfig(
    input_schema=SearchRequestSchema(),
    input_dto_class=SearchRequestDTO,
    primary_output_schema=SearchResponseSchema(),
)