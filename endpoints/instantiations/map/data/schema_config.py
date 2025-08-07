from endpoints.instantiations.map.data.schema import DataMapResponseSchema
from endpoints.schema_config.config.core import EndpointSchemaConfig

LocationsDataEndpointSchemaConfig = EndpointSchemaConfig(
    primary_output_schema=DataMapResponseSchema(),
)