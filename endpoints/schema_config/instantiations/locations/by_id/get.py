from endpoints.schema_config.helpers import get_get_by_id_endpoint_schema_config
from middleware.schema_and_dto.schemas.locations.by_id import (
    GetLocationInfoByIDResponseSchema,
)

LocationsByIDGetEndpointSchemaConfig = get_get_by_id_endpoint_schema_config(
    primary_output_schema=GetLocationInfoByIDResponseSchema(),
)
