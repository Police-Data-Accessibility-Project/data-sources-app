from marshmallow import Schema

from middleware.schema_and_dto.schemas.locations._helpers import (
    LOCATION_TYPE_FIELD,
    STATE_NAME_FIELD,
    STATE_ISO_FIELD,
    COUNTY_FIPS_FIELD,
    COUNTY_NAME_FIELD,
    LOCALITY_NAME_FIELD,
    DISPLAY_NAME_FIELD,
    LOCATION_ID_FIELD,
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
