from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.schemas.notifications_.preview import (
    NotificationsPreviewResponseSchema,
)

NotificationsPreviewEndpointSchemaConfig = EndpointSchemaConfig(
    primary_output_schema=NotificationsPreviewResponseSchema(),
)
