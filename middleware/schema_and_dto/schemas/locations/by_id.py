from middleware.schema_and_dto.schemas.locations._helpers import (
    DISPLAY_NAME_FIELD,
)
from middleware.schema_and_dto.schemas.locations.info.expanded import (
    LocationInfoExpandedSchema,
)


class GetLocationInfoByIDResponseSchema(LocationInfoExpandedSchema):
    display_name = DISPLAY_NAME_FIELD
