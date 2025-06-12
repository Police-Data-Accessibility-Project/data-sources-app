from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.schemas.locations.map.response import (
    LocationsMapResponseSchema,
)

LocationsMapEndpointSchemaConfig = EndpointSchemaConfig(
    primary_output_schema=LocationsMapResponseSchema(),
)
