from marshmallow import fields

from middleware.schema_and_dto_logic.common_response_schemas import (
    GetManyResponseSchemaBase,
)
from middleware.schema_and_dto_logic.schemas.admin.base import AdminUserBaseSchema
from middleware.schema_and_dto_logic.util import get_json_metadata


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
