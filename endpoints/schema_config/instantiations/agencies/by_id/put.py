from endpoints.schema_config.helpers import get_put_resource_endpoint_schema_config
from endpoints.instantiations.agencies_.put.schemas.outer import AgenciesPutSchema

AgenciesByIDPutEndpointSchemaConfig = get_put_resource_endpoint_schema_config(
    input_schema=AgenciesPutSchema(),
)
