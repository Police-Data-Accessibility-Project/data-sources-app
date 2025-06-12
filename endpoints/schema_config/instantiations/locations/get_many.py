from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.dtos.locations.get import LocationsGetRequestDTO
from middleware.schema_and_dto.schemas.locations.get_many.request import (
    LocationsGetManyRequestSchema,
)
from middleware.schema_and_dto.schemas.locations.get_many.response import (
    LocationsGetManyResponseSchema,
)

LocationsGetManyEndpointSchemaConfig = EndpointSchemaConfig(
    input_schema=LocationsGetManyRequestSchema(),
    input_dto_class=LocationsGetRequestDTO,
    primary_output_schema=LocationsGetManyResponseSchema(),
)
