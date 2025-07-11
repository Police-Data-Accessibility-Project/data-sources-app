from typing import final


from middleware.schema_and_dto.schemas.common.common_response_schemas import (
    MessageSchema,
)
from middleware.schema_and_dto.schemas.helpers import int_field


@final
class NotificationsResponseSchema(MessageSchema):
    count = int_field("The number of notification batches sent.")
