from marshmallow import fields

from middleware.schema_and_dto.schemas.common.common_response_schemas import (
    GetManyResponseSchemaBase,
)
from middleware.schema_and_dto.schemas.admin.base import AdminUserBaseSchema
from middleware.schema_and_dto.util import get_json_metadata


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
