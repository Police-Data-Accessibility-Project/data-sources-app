from marshmallow import fields

from db.enums import ApprovalStatus
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    GetManyRequestsBaseSchema,
)
from utilities.enums import SourceMappingEnum


class DataSourcesGetManyRequestSchema(GetManyRequestsBaseSchema):
    approval_status = fields.Enum(
        enum=ApprovalStatus,
        by_value=fields.String,
        required=False,
        metadata={
            "source": SourceMappingEnum.QUERY_ARGS,
            "description": "The approval status of the data sources.",
            "default": "approved",
        },
    )
