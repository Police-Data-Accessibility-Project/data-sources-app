from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.schemas.user_profile.response import (
    UserProfileResponseSchema,
)

UserProfileGetEndpointSchemaConfig = EndpointSchemaConfig(
    primary_output_schema=UserProfileResponseSchema(),
)
