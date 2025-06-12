from marshmallow import fields, validate

from db.enums import LocationType
from middleware.schema_and_dto.enums import CSVColumnCondition
from middleware.schema_and_dto.util import get_json_metadata
from utilities.enums import SourceMappingEnum

STATE_ISO_FIELD = fields.Str(
    required=False,
    allow_none=True,
    metadata={
        "description": "The 2 letter ISO code of the state.",
        "source": SourceMappingEnum.JSON,
        "csv_column_name": CSVColumnCondition.SAME_AS_FIELD,
    },
    validate=validate.Length(2),
)
COUNTY_FIPS_FIELD = fields.Str(
    required=False,
    allow_none=True,
    metadata={
        "description": "The unique 5-digit FIPS code of the county."
        "Does not apply to state or federal agencies.",
        "source": SourceMappingEnum.JSON,
        "csv_column_name": CSVColumnCondition.SAME_AS_FIELD,
    },
    validate=validate.Length(5),
)
LOCALITY_NAME_FIELD = fields.Str(
    required=False,
    allow_none=True,
    metadata={
        "description": "The name of the locality.",
        "source": SourceMappingEnum.JSON,
        "csv_column_name": CSVColumnCondition.SAME_AS_FIELD,
    },
)
LOCATION_ID_FIELD = fields.Integer(
    metadata=get_json_metadata(
        description="The unique identifier of the location.",
    )
)
LOCATION_TYPE_FIELD = fields.Enum(
    required=True,
    enum=LocationType,
    by_value=fields.Str,
    metadata={
        "description": "The type of location. ",
        "source": SourceMappingEnum.JSON,
        "csv_column_name": "location_type",
    },
)
STATE_NAME_FIELD = fields.Str(
    required=True,
    allow_none=True,
    metadata=get_json_metadata(description="The name of the state."),
)
COUNTY_NAME_FIELD = fields.Str(
    required=True,
    allow_none=True,
    metadata=get_json_metadata(description="The name of the county."),
)
DISPLAY_NAME_FIELD = fields.Str(
    required=True,
    metadata=get_json_metadata(description="The display name for the location"),
)
