from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.schemas.notifications import NotificationsResponseSchema

NotificationsPostEndpointSchemaConfig = EndpointSchemaConfig(
    primary_output_schema=NotificationsResponseSchema(),
)
