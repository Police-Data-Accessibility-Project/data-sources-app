from marshmallow import fields, Schema

from middleware.enums import JurisdictionType, AgencyType
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    STATE_ISO_FIELD,
    COUNTY_FIPS_FIELD,
    LOCALITY_NAME_FIELD,
)
from middleware.schema_and_dto_logic.enums import CSVColumnCondition
from utilities.enums import SourceMappingEnum


def get_submitted_name_field(required: bool) -> fields.Str:
    return fields.Str(
        required=required,
        metadata={
            "description": "The name of the agency.",
            "source": SourceMappingEnum.JSON,
            "csv_column_name": CSVColumnCondition.SAME_AS_FIELD,
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
            "csv_column_name": CSVColumnCondition.SAME_AS_FIELD,
        },
    )


class AgencyInfoBaseSchema(Schema):
    homepage_url = fields.Str(
        allow_none=True,
        metadata={
            "description": "The URL of the agency's homepage.",
            "source": SourceMappingEnum.JSON,
            "csv_column_name": CSVColumnCondition.SAME_AS_FIELD,
        },
    )
    lat = fields.Float(
        required=False,
        allow_none=True,
        metadata={
            "description": "The latitude of the agency's location.",
            "source": SourceMappingEnum.JSON,
            "csv_column_name": CSVColumnCondition.SAME_AS_FIELD,
        },
    )
    lng = fields.Float(
        required=False,
        allow_none=True,
        metadata={
            "description": "The longitude of the agency's location.",
            "source": SourceMappingEnum.JSON,
            "csv_column_name": CSVColumnCondition.SAME_AS_FIELD,
        },
    )
    defunct_year = fields.Str(
        required=False,
        allow_none=True,
        metadata={
            "description": "If present, denotes an agency which has defunct but may still have relevant records.",
            "source": SourceMappingEnum.JSON,
            "csv_column_name": CSVColumnCondition.SAME_AS_FIELD,
        },
    )
    agency_type = fields.Enum(
        required=False,
        enum=AgencyType,
        by_value=fields.Str,
        allow_none=True,
        load_default=AgencyType.NONE,
        metadata={
            "description": "The type of agency.",
            "source": SourceMappingEnum.JSON,
            "csv_column_name": CSVColumnCondition.SAME_AS_FIELD,
        },
    )
    multi_agency = fields.Bool(
        required=False,
        load_default=False,
        metadata={
            "description": "Whether the agency is a multi-agency.",
            "source": SourceMappingEnum.JSON,
            "csv_column_name": CSVColumnCondition.SAME_AS_FIELD,
        },
    )
    zip_code = fields.Str(
        required=False,
        allow_none=True,
        metadata={
            "description": "The zip code of the agency's location.",
            "source": SourceMappingEnum.JSON,
            "csv_column_name": CSVColumnCondition.SAME_AS_FIELD,
        },
        # TODO: Re-enable when all zip codes are of expected length
        # validate=validate.Length(min=5),
    )
    no_web_presence = fields.Bool(
        required=False,
        load_default=False,
        metadata={
            "description": "True when an agency does not have a dedicated website.",
            "source": SourceMappingEnum.JSON,
            "csv_column_name": CSVColumnCondition.SAME_AS_FIELD,
        },
    )
    approved = fields.Bool(
        required=False,
        load_default=False,
        metadata={
            "description": "Whether the agency is approved.",
            "source": SourceMappingEnum.JSON,
        },
    )
    rejection_reason = fields.Str(
        required=False,
        allow_none=True,
        metadata={
            "description": "The reason the agency was rejected.",
            "source": SourceMappingEnum.JSON,
        },
    )
    last_approval_editor = fields.String(
        required=False,
        allow_none=True,
        metadata={
            "description": "The user who last approved or rejected the agency.",
            "source": SourceMappingEnum.JSON,
        },
    )
    submitter_contact = fields.Str(
        required=False,
        allow_none=True,
        metadata={
            "description": "The contact information of the user who submitted the agency.",
            "source": SourceMappingEnum.JSON,
            "csv_column_name": CSVColumnCondition.SAME_AS_FIELD,
        },
    )


class AgenciesExpandedSchema(AgencyInfoBaseSchema):
    id = fields.Integer(
        required=True,
        metadata={
            "description": "The id of the agency.",
            "source": SourceMappingEnum.JSON,
        },
    )
    submitted_name = get_submitted_name_field(required=True)
    jurisdiction_type = get_jurisdiction_type_field(required=True)
    name = fields.Str(
        required=False,
        metadata={
            "description": "The name of the agency. If a state is provided, "
            "concatenates `submitted_name` + ` - ` + `state_iso` "
            "to help differentiate agencies with similar names.",
            "source": SourceMappingEnum.JSON,
        },
    )
    state_iso = STATE_ISO_FIELD
    state_name = fields.Str(
        required=False,
        allow_none=True,
        metadata={
            "description": "The name of the state in which the agency is located. Does not apply to federal agencies",
            "source": SourceMappingEnum.JSON,
        },
    )
    county_name = fields.Str(
        required=False,
        allow_none=True,
        metadata={
            "description": "The name of the county in which the agency is located.",
            "source": SourceMappingEnum.JSON,
        },
    )
    county_fips = COUNTY_FIPS_FIELD
    locality_name = LOCALITY_NAME_FIELD
    airtable_agency_last_modified = fields.DateTime(
        required=False,
        format="iso",
        metadata={
            "description": "When the agency was last modified",
            "source": SourceMappingEnum.JSON,
        },
    )
    agency_created = fields.DateTime(
        required=False,
        format="iso",
        metadata={
            "description": "When the agency was created",
            "source": SourceMappingEnum.JSON,
        },
    )
