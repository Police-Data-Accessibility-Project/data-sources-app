from marshmallow import Schema, fields

from middleware.schema_and_dto_logic.common_response_schemas import MessageSchema
from utilities.enums import SourceMappingEnum


class NotificationsResponseSchema(MessageSchema):
    count = fields.Int(
        required=True,
        metadata={
            "description": "The number of notification batches sent.",
            "source": SourceMappingEnum.JSON,
        },
    )
