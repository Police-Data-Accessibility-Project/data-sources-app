from marshmallow import Schema, fields

from middleware.enums import PermissionsEnum
from middleware.schema_and_dto.util import get_json_metadata


class AdminUserBaseSchema(Schema):
    user_id = fields.Integer(
        required=True, metadata=get_json_metadata("The ID of the user")
    )
    email = fields.Email(
        required=True, metadata=get_json_metadata("The email of the user")
    )
    permissions = fields.List(
        fields.Enum(
            PermissionsEnum,
            by_value=True,
            metadata=get_json_metadata("The permissions of the user"),
        ),
        required=True,
        metadata=get_json_metadata("The permissions of the user"),
    )
    created_at = fields.DateTime(
        required=True,
        metadata=get_json_metadata("The date and time the user was created"),
    )
    updated_at = fields.DateTime(
        required=True,
        metadata=get_json_metadata("The date and time the user was updated"),
    )
