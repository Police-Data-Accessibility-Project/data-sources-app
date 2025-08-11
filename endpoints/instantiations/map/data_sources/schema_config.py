from endpoints.schema_config.config.core import EndpointSchemaConfig
from endpoints.instantiations.map.data_sources.schemas.outer import (
    DataSourcesMapResponseSchema,
)

DataSourcesMapEndpointSchemaConfig = EndpointSchemaConfig(
    primary_output_schema=DataSourcesMapResponseSchema(),
)
