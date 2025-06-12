from middleware.schema_and_dto.schemas.locations._helpers import (
    STATE_NAME_FIELD,
    COUNTY_NAME_FIELD,
)
from middleware.schema_and_dto.schemas.locations.info.base import (
    LocationInfoSchema,
)


class LocationInfoExpandedSchema(LocationInfoSchema):
    state_name = STATE_NAME_FIELD
    county_name = COUNTY_NAME_FIELD
