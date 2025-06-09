from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.schemas.agencies.related_location import (
    AgenciesRelatedLocationSchema,
)
from middleware.schema_and_dto.schemas.common.common_response_schemas import (
    MessageSchema,
)

AgenciesByIDRelatedLocationsDeleteEndpointSchemaConfig = EndpointSchemaConfig(
    input_schema=AgenciesRelatedLocationSchema(),
    primary_output_schema=MessageSchema(),
)
