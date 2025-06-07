from marshmallow import Schema, fields

from middleware.enums import PermissionsEnum
from middleware.schema_and_dto_logic.common_response_schemas import (
    GetManyResponseSchemaBase,
)
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    GetByIDBaseSchema,
)
from middleware.schema_and_dto_logic.dynamic_logic.pydantic_to_marshmallow.core import (
    generate_marshmallow_schema,
)
from middleware.schema_and_dto_logic.dtos.admin_dtos import (
    AdminUserPutDTO,
)
from middleware.schema_and_dto_logic.util import get_json_metadata


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


class AdminUsersGetManyResponseSchema(GetManyResponseSchemaBase):
    data = fields.List(
        fields.Nested(
            AdminUserBaseSchema(),
            required=True,
            metadata=get_json_metadata(description="The list of admin users"),
        ),
        required=True,
        metadata=get_json_metadata(description="The list of admin users"),
    )


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


AdminUsersPutSchema = generate_marshmallow_schema(AdminUserPutDTO)


class AdminUsersGetByIDResponseSchema(GetByIDBaseSchema):
    data = fields.Nested(
        AdminUserBaseSchema(),
        required=True,
        metadata=get_json_metadata(description="The admin user"),
    )


class AdminUsersGetByIDSchema(AdminUserBaseSchema):
    pass
