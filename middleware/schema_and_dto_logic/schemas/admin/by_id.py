from marshmallow import fields

from middleware.schema_and_dto_logic.schemas.common.base import GetByIDBaseSchema
from middleware.schema_and_dto_logic.schemas.admin.base import AdminUserBaseSchema
from middleware.schema_and_dto_logic.util import get_json_metadata


class AdminUsersGetByIDResponseSchema(GetByIDBaseSchema):
    data = fields.Nested(
        AdminUserBaseSchema(),
        required=True,
        metadata=get_json_metadata(description="The admin user"),
    )
