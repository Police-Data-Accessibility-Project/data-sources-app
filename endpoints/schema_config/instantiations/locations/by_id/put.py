from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.dtos.locations.put import LocationPutDTO
from middleware.schema_and_dto.schemas.common.common_response_schemas import (
    MessageSchema,
)
from middleware.schema_and_dto.schemas.locations.put import LocationPutSchema

LocationsByIDPutEndpointSchemaConfig = EndpointSchemaConfig(
    input_schema=LocationPutSchema(),
    input_dto_class=LocationPutDTO,
    primary_output_schema=MessageSchema(),
)
