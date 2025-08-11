from endpoints.schema_config.helpers import get_get_by_id_endpoint_schema_config
from endpoints.instantiations.agencies_.get.by_id.core.schemas.response import (
    AgenciesGetByIDResponseSchema,
)

AgenciesByIDGetEndpointSchemaConfig = get_get_by_id_endpoint_schema_config(
    primary_output_schema=AgenciesGetByIDResponseSchema(),
)
