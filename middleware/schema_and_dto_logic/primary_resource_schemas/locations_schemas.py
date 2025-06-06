from marshmallow import Schema, fields, validate, validates_schema, ValidationError

from db.enums import LocationType
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    GetManyRequestsBaseSchema,
)
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


class LocationInfoResponseSchema(Schema):
    type = LOCATION_TYPE_FIELD
    state_name = STATE_NAME_FIELD
    state_iso = STATE_ISO_FIELD
    county_name = COUNTY_FIPS_FIELD
    county_fips = COUNTY_NAME_FIELD
    locality_name = LOCALITY_NAME_FIELD
    display_name = DISPLAY_NAME_FIELD
    location_id = LOCATION_ID_FIELD


class LocationInfoSchema(Schema):
    type = LOCATION_TYPE_FIELD
    state_iso = STATE_ISO_FIELD
    county_fips = COUNTY_FIPS_FIELD
    locality_name = LOCALITY_NAME_FIELD
    location_id = LOCATION_ID_FIELD

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
    state_name = STATE_NAME_FIELD
    county_name = COUNTY_NAME_FIELD


class LatLngSchema(Schema):
    lat = fields.Float(
        required=True,
        allow_none=True,
        metadata=get_json_metadata("The latitude of the location"),
    )
    lng = fields.Float(
        required=True,
        allow_none=True,
        metadata=get_json_metadata("The longitude of the location"),
    )


class LocationInfoGetManyInnerSchema(LocationInfoExpandedSchema):
    coordinates = fields.Nested(
        LatLngSchema(),
        required=True,
        metadata=get_json_metadata("The latitude and longitude of the location"),
    )


class GetLocationInfoByIDResponseSchema(LocationInfoExpandedSchema):
    display_name = DISPLAY_NAME_FIELD


class LocationsGetManySchema(Schema):
    results = fields.List(
        fields.Nested(
            LocationInfoGetManyInnerSchema(),
            required=True,
            metadata=get_json_metadata("The list of results"),
        ),
        required=True,
        metadata=get_json_metadata("The list of results"),
    )


class LocationPutSchema(Schema):
    latitude = fields.Float(
        required=True,
        allow_none=True,
        metadata=get_json_metadata("The latitude of the location"),
    )
    longitude = fields.Float(
        required=True,
        allow_none=True,
        metadata=get_json_metadata("The longitude of the location"),
    )


class LocalitiesLocationsMapInnerSchema(Schema):
    source_count = fields.Int(
        metadata=get_json_metadata("The number of data sources for the locality")
    )
    name = fields.Str(metadata=get_json_metadata("The name of the locality"))
    location_id = fields.Integer(metadata=get_json_metadata("The id of the locality"))
    county_name = fields.Str(metadata=get_json_metadata("The name of the county"))
    county_fips = fields.Str(metadata=get_json_metadata("The fips code of the county"))
    state_iso = fields.Str(metadata=get_json_metadata("The iso code of the state"))
    coordinates = fields.Nested(
        LatLngSchema(),
        required=True,
        metadata=get_json_metadata("The latitude and longitude of the location"),
    )


class CountiesLocationsMapInnerSchema(Schema):
    source_count = fields.Int(
        metadata=get_json_metadata("The number of data sources for the county")
    )
    name = fields.Str(metadata=get_json_metadata("The name of the county"))
    location_id = fields.Integer(metadata=get_json_metadata("The id of the county"))
    state_iso = fields.Str(metadata=get_json_metadata("The iso code of the state"))
    fips = fields.Str(metadata=get_json_metadata("The fips code of the county"))


class StatesLocationsMapInnerSchema(Schema):
    source_count = fields.Int(
        metadata=get_json_metadata("The number of data sources for the state")
    )
    name = fields.Str(metadata=get_json_metadata("The name of the state"))
    state_iso = fields.Str(metadata=get_json_metadata("The iso code of the state"))
    location_id = fields.Integer(metadata=get_json_metadata("The id of the state"))


class LocationsMapResponseSchema(Schema):
    localities = fields.List(
        fields.Nested(
            LocalitiesLocationsMapInnerSchema(),
            required=True,
            metadata=get_json_metadata("The list of localities"),
        ),
        required=True,
        metadata=get_json_metadata("The list of localities"),
    )
    counties = fields.List(
        fields.Nested(
            CountiesLocationsMapInnerSchema(),
            required=True,
            metadata=get_json_metadata("The list of counties"),
        ),
        required=True,
        metadata=get_json_metadata("The list of counties"),
    )
    states = fields.List(
        fields.Nested(
            StatesLocationsMapInnerSchema(),
            required=True,
            metadata=get_json_metadata("The list of states"),
        ),
        required=True,
        metadata=get_json_metadata("The list of states"),
    )


class LocationsGetManyRequestSchema(Schema):
    page = fields.Integer(
        validate=validate.Range(min=1),
        load_default=1,
        metadata={
            "description": "The page number of the results to retrieve. Begins at 1.",
            "source": SourceMappingEnum.QUERY_ARGS,
        },
    )
    type = fields.Enum(
        required=False,
        allow_none=True,
        enum=LocationType,
        by_value=fields.Str,
        metadata={
            "description": "The type of location. ",
            "source": SourceMappingEnum.QUERY_ARGS,
        },
    )
    has_coordinates = fields.Boolean(
        required=False,
        allow_none=True,
        metadata={
            "description": "Whether or not the location has coordinates",
            "source": SourceMappingEnum.QUERY_ARGS,
        },
    )
