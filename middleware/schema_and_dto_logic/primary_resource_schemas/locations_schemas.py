from marshmallow import Schema, fields, validate, validates_schema, ValidationError

from database_client.enums import LocationType
from middleware.schema_and_dto_logic.enums import CSVColumnCondition
from middleware.schema_and_dto_logic.util import get_json_metadata
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


class LocationInfoSchema(Schema):
    type = fields.Enum(
        required=True,
        enum=LocationType,
        by_value=fields.Str,
        metadata={
            "description": "The type of location. ",
            "source": SourceMappingEnum.JSON,
            "csv_column_name": "location_type",
        },
    )
    state_iso = STATE_ISO_FIELD
    county_fips = COUNTY_FIPS_FIELD
    locality_name = LOCALITY_NAME_FIELD
    id = fields.Integer(
        metadata=get_json_metadata(
            description="The unique identifier of the location.",
        )
    )

    @validates_schema
    def validate_location_fields(self, data, **kwargs):
        location_type = data.get("type")

        if location_type == LocationType.STATE:
            if data.get("state_iso") is None:
                raise ValidationError("state_iso is required for location type STATE.")
            if (
                data.get("county_fips") is not None
                or data.get("locality_name") is not None
            ):
                raise ValidationError(
                    "county_fips and locality_name must be None for location type STATE."
                )

        elif location_type == LocationType.COUNTY:
            if data.get("county_fips") is None:
                raise ValidationError(
                    "county_fips is required for location type COUNTY."
                )
            if data.get("state_iso") is None:
                raise ValidationError("state_iso is required for location type COUNTY.")
            if data.get("locality_name"):
                raise ValidationError(
                    "locality_name must be None for location type COUNTY."
                )

        elif location_type == LocationType.LOCALITY:
            if data.get("locality_name") is None:
                raise ValidationError(
                    "locality_name is required for location type CITY."
                )
            if data.get("state_iso") is None:
                raise ValidationError("state_iso is required for location type CITY.")
            if data.get("county_fips") is None:
                raise ValidationError("county_fips is required for location type CITY.")


class LocationInfoExpandedSchema(LocationInfoSchema):
    state_name = fields.Str(
        required=True, metadata=get_json_metadata(description="The name of the state.")
    )
    county_name = fields.Str(
        required=True,
        allow_none=True,
        metadata=get_json_metadata(description="The name of the county."),
    )
