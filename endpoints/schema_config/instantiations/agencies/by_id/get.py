from endpoints.schema_config.helpers import get_get_by_id_endpoint_schema_config
from middleware.schema_and_dto.schemas.agencies.get.by_id.response import (
    AgenciesGetByIDResponseSchema,
)

AgenciesByIDGetEndpointSchemaConfig = get_get_by_id_endpoint_schema_config(
    primary_output_schema=AgenciesGetByIDResponseSchema(),
)
