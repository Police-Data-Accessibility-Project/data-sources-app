from marshmallow import fields

from middleware.schema_and_dto.schemas.agencies.base import AgencyInfoBaseSchema
from middleware.schema_and_dto.schemas.agencies.helpers import (
    get_name_field,
    get_jurisdiction_type_field,
)
from endpoints.instantiations.data_sources_._shared.schemas.expanded import (
    DataSourceExpandedSchema,
)
from endpoints.instantiations.locations_._shared.schemas.response import (
    LocationInfoResponseSchema,
)
from middleware.schema_and_dto.schemas.locations._helpers import (
    STATE_ISO_FIELD,
    COUNTY_FIPS_FIELD,
    LOCALITY_NAME_FIELD,
)
from middleware.schema_and_dto.util import get_json_metadata
from utilities.enums import SourceMappingEnum


class AgenciesGetSchema(AgencyInfoBaseSchema):
    id = fields.Integer(
        required=True,
        metadata={
            "description": "The id of the agency.",
            "source": SourceMappingEnum.JSON,
        },
    )
    submitted_name = get_name_field(required=True)
    jurisdiction_type = get_jurisdiction_type_field(required=True)
    name = fields.Str(
        required=False,
        metadata={
            "description": "The name of the agency.",
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
    data_sources = fields.List(
        cls_or_instance=fields.Nested(
            nested=DataSourceExpandedSchema(only=["id", "name"]),
            required=True,
            metadata=get_json_metadata(
                description="The data sources associated with the agency",
            ),
        ),
        required=True,
        metadata=get_json_metadata(
            description="The data sources associated with the agency",
        ),
    )
    locations = fields.List(
        cls_or_instance=fields.Nested(
            nested=LocationInfoResponseSchema(),
            required=True,
            metadata=get_json_metadata(
                description="The locations associated with the agency",
            ),
        ),
        required=True,
        metadata=get_json_metadata(
            description="The locations associated with the agency",
        ),
    )
