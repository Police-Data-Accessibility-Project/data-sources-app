from marshmallow import Schema, fields

from middleware.enums import AgencyType
from middleware.schema_and_dto_logic.dynamic_logic.dynamic_csv_to_schema_conversion_logic import (
    generate_flat_csv_schema,
)
from middleware.schema_and_dto_logic.schemas.agencies.helpers import (
    get_name_field,
    get_jurisdiction_type_field,
)
from middleware.schema_and_dto_logic.schemas.agencies.post import AgenciesPostSchema
from utilities.enums import SourceMappingEnum

AgenciesPostRequestFlatBaseSchema = generate_flat_csv_schema(
    schema=AgenciesPostSchema()
)


class AgenciesPostRequestFlatSchema(Schema):
    name = get_name_field(required=True)
    jurisdiction_type = get_jurisdiction_type_field(required=True)
    homepage_url = fields.Str(
        allow_none=True,
        metadata={
            "description": "The URL of the agency's homepage.",
            "source": SourceMappingEnum.JSON,
        },
    )
    lat = fields.Float(
        required=False,
        allow_none=True,
        metadata={
            "description": "The latitude of the agency's location.",
            "source": SourceMappingEnum.JSON,
        },
    )
    lng = fields.Float(
        required=False,
        allow_none=True,
        metadata={
            "description": "The longitude of the agency's location.",
            "source": SourceMappingEnum.JSON,
        },
    )
    defunct_year = fields.Str(
        required=False,
        allow_none=True,
        metadata={
            "description": "If present, denotes an agency which has defunct but may still have relevant records.",
            "source": SourceMappingEnum.JSON,
        },
    )
    agency_type = fields.Enum(
        required=True,
        enum=AgencyType,
        by_value=fields.Str,
        allow_none=True,
        metadata={
            "description": "The type of agency.",
            "source": SourceMappingEnum.JSON,
        },
    )
    multi_agency = fields.Bool(
        required=False,
        load_default=False,
        metadata={
            "description": "Whether the agency is a multi-agency.",
            "source": SourceMappingEnum.JSON,
        },
    )
    no_web_presence = fields.Bool(
        required=False,
        load_default=False,
        metadata={
            "description": "True when an agency does not have a dedicated website.",
            "source": SourceMappingEnum.JSON,
        },
    )
    submitter_contact = fields.Str(
        required=False,
        allow_none=True,
        metadata={
            "description": "The contact information of the user who submitted the agency.",
            "source": SourceMappingEnum.JSON,
        },
    )
    location_id = fields.Integer(
        required=False,
        allow_none=True,
        metadata={
            "description": "The id of the location of the agency.",
            "source": SourceMappingEnum.JSON,
        },
    )
