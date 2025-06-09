from marshmallow import fields

from db.enums import ApprovalStatus
from middleware.schema_and_dto_logic.dtos.common.base import GetManyRequestsBaseSchema
from middleware.schema_and_dto_logic.util import get_query_metadata


class GetManyAgenciesRequestsSchema(GetManyRequestsBaseSchema):
    approval_status = fields.Enum(
        enum=ApprovalStatus,
        by_value=fields.Str,
        allow_none=True,
        metadata=get_query_metadata("The approval status of the agencies to return."),
    )
