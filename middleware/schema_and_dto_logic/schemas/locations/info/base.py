from marshmallow import Schema, validates_schema, ValidationError

from db.enums import LocationType
from middleware.schema_and_dto_logic.schemas.locations._helpers import (
    LOCATION_TYPE_FIELD,
    STATE_ISO_FIELD,
    COUNTY_FIPS_FIELD,
    LOCALITY_NAME_FIELD,
    LOCATION_ID_FIELD,
)


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
