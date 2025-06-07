from marshmallow import Schema, fields

from middleware.enums import PermissionsEnum
from middleware.schema_and_dto_logic.util import get_json_metadata


class AdminUsersPostSchema(Schema):
    email = fields.Email(
        required=True,
        metadata=get_json_metadata(description="The email of the admin user"),
    )
    password = fields.String(
        required=True,
        metadata=get_json_metadata(description="The password of the admin user"),
    )
    permissions = fields.List(
        fields.Enum(
            PermissionsEnum,
            by_value=True,
            metadata=get_json_metadata(description="The permissions of the admin user"),
        ),
        required=True,
        metadata=get_json_metadata(description="The permissions of the admin user"),
    )
