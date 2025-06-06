from marshmallow import fields, Schema, pre_load

from db.enums import ApprovalStatus, RequestStatus
from middleware.enums import JurisdictionType, AgencyType
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    GetManyRequestsBaseSchema,
)
from middleware.schema_and_dto_logic.dynamic_logic.pydantic_to_marshmallow.core import (
    generate_marshmallow_schema,
)
from middleware.schema_and_dto_logic.primary_resource_dtos.agencies_dtos import (
    AgencyInfoBaseDTO,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.locations_schemas import (
    STATE_ISO_FIELD,
    COUNTY_FIPS_FIELD,
    LOCALITY_NAME_FIELD,
)
from middleware.schema_and_dto_logic.enums import CSVColumnCondition
from middleware.schema_and_dto_logic.util import get_query_metadata
from utilities.enums import SourceMappingEnum


def get_name_field(required: bool) -> fields.Str:
    return fields.Str(
        required=required,
        metadata={
            "description": "The name of the agency.",
            "source": SourceMappingEnum.JSON,
        },
    )


def get_jurisdiction_type_field(required: bool) -> fields.Enum:
    return fields.Enum(
        required=required,
        enum=JurisdictionType,
        by_value=fields.Str,
        metadata={
            "description": "The highest level of jurisdiction of the agency.",
            "source": SourceMappingEnum.JSON,
        },
    )


AgencyInfoBaseSchema = generate_marshmallow_schema(AgencyInfoBaseDTO)


class GetManyAgenciesRequestsSchema(GetManyRequestsBaseSchema):
    approval_status = fields.Enum(
        enum=ApprovalStatus,
        by_value=fields.Str,
        allow_none=True,
        metadata=get_query_metadata("The approval status of the agencies to return."),
    )
