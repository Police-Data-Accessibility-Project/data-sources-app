from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.schemas.api_key import APIKeyResponseSchema

ApiKeyPostEndpointSchemaConfig = EndpointSchemaConfig(
    primary_output_schema=APIKeyResponseSchema(),
)
