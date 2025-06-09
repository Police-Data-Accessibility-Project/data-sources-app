from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.dtos.metrics import (
    MetricsFollowedSearchesBreakdownRequestDTO,
)
from middleware.schema_and_dto.schemas.metrics.breakdown.request import (
    MetricsFollowedSearchesBreakdownRequestSchema,
)
from middleware.schema_and_dto.schemas.metrics.breakdown.response import (
    MetricsFollowedSearchesBreakdownOuterSchema,
)

MetricsFollowedSearchesBreakdownGetEndpointSchemaConfig = EndpointSchemaConfig(
    input_schema=MetricsFollowedSearchesBreakdownRequestSchema(),
    input_dto_class=MetricsFollowedSearchesBreakdownRequestDTO,
    primary_output_schema=MetricsFollowedSearchesBreakdownOuterSchema(),
)
