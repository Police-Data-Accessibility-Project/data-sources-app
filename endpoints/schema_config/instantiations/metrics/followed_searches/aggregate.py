from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.schemas.metrics.aggregate import (
    MetricsFollowedSearchesAggregateResponseSchema,
)

MetricsFollowedSearchesAggregateGetEndpointSchemaConfig = EndpointSchemaConfig(
    primary_output_schema=MetricsFollowedSearchesAggregateResponseSchema(),
)
