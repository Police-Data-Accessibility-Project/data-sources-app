from marshmallow import Schema, fields

from middleware.enums import ContactFormMessageType
from middleware.schema_and_dto_logic.util import get_json_metadata


class ContactFormPostSchema(Schema):
    email = fields.Email(
        required=True, metadata=get_json_metadata("The email of the user")
    )
    message = fields.String(
        required=True, metadata=get_json_metadata("The message of the user")
    )
    type = fields.Enum(
        enum=ContactFormMessageType,
        by_value=True,
        required=True,
        metadata=get_json_metadata("The type of message"),
    )
