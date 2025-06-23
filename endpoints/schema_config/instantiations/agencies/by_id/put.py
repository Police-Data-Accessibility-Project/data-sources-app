from endpoints.schema_config.helpers import get_put_resource_endpoint_schema_config
from middleware.schema_and_dto.schemas.agencies.put import AgenciesPutSchema

AgenciesByIDPutEndpointSchemaConfig = get_put_resource_endpoint_schema_config(
    input_schema=AgenciesPutSchema(),
)
