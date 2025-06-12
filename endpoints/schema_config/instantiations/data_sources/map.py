from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.schemas.data_sources.map.outer import (
    DataSourcesMapResponseSchema,
)

DataSourcesMapEndpointSchemaConfig = EndpointSchemaConfig(
    primary_output_schema=DataSourcesMapResponseSchema(),
)
