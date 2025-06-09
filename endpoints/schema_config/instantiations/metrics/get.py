from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.schemas.metrics.get import MetricsGetResponseSchema

MetricsGetEndpointSchemaConfig = EndpointSchemaConfig(
    primary_output_schema=MetricsGetResponseSchema(),
)
