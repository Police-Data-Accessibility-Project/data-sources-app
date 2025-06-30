from middleware.schema_and_dto.dtos.notifications.preview import (
    NotificationsPreviewOutput,
)
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    pydantic_to_marshmallow,
)

NotificationsPreviewResponseSchema = pydantic_to_marshmallow(NotificationsPreviewOutput)
