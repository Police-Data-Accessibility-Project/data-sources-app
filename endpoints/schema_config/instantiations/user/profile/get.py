from endpoints.schema_config.config.core import EndpointSchemaConfig
from endpoints.instantiations.user.by_id.get.schema import UserProfileResponseSchema

UserProfileGetEndpointSchemaConfig = EndpointSchemaConfig(
    primary_output_schema=UserProfileResponseSchema(),
)
