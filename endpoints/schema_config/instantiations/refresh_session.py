from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.schemas.auth.login import LoginResponseSchema

RefreshSessionEndpointSchemaConfig = EndpointSchemaConfig(
    primary_output_schema=LoginResponseSchema(),
)
