from marshmallow import Schema, fields, validates_schema
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    GetManyRequestsBaseSchema,
)
from middleware.enums import PermissionsEnum


class AdminUserBaseSchema(GetManyRequestsBaseSchema):
    user_id = fields.Integer(
        required=True, metadata={"description": "The ID of the admin user"}
    )
    email = fields.Email(
        required=True, metadata={"description": "The email of the admin user"}
    )
    permissions = fields.List(
        fields.Enum(PermissionsEnum, by_value=True),
        required=True,
        metadata={"description": "The permissions of the admin user"},
    )
    created_at = fields.DateTime(
        required=True,
        metadata={"description": "The date and time the admin user was created"},
    )


from marshmallow import Schema, fields
from middleware.schema_and_dto_logic.common_response_schemas import (
    MessageSchema,
    GetManyResponseSchemaBase,
)
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    GetByIDBaseSchema,
)

from middleware.schema_and_dto_logic.util import get_json_metadata


class AdminUsersGetManyResponseSchema(GetManyResponseSchemaBase):
    data = fields.List(
        fields.Nested(AdminUserBaseSchema(), required=True),
        required=True,
        metadata=get_json_metadata(description="The list of admin users"),
    )


class AdminUsersPostSchema(AdminUserBaseSchema):
    email = fields.Email(
        required=True, metadata={"description": "The email of the admin user"}
    )
    password = fields.String(
        required=True, metadata={"description": "The password of the admin user"}
    )
    permissions = fields.List(
        fields.Enum(PermissionsEnum, by_value=True),
        required=True,
        metadata={"description": "The permissions of the admin user"},
    )


class AdminUsersPutSchema(AdminUserBaseSchema):
    password = fields.String(
        required=False,
        metadata={"description": "The new password of the admin user"},
    )


class AdminUsersGetByIDResponseSchema(GetByIDBaseSchema):
    data = fields.Nested(
        AdminUserBaseSchema(),
        required=True,
        metadata=get_json_metadata(description="The admin user"),
    )


class AdminUsersGetByIDSchema(AdminUserBaseSchema):
    pass
