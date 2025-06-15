from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.primary_resource_logic.unique_url_checker import (
    UniqueURLCheckerRequestSchema,
    UniqueURLCheckerResponseOuterSchema,
    UniqueURLCheckerRequestDTO,
)

UniqueURLCheckerEndpointSchemaConfig = EndpointSchemaConfig(
    input_schema=UniqueURLCheckerRequestSchema(),
    primary_output_schema=UniqueURLCheckerResponseOuterSchema(),
    input_dto_class=UniqueURLCheckerRequestDTO,
)
