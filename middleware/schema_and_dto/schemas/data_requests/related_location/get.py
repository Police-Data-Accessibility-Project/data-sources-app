from middleware.schema_and_dto.schemas.schema_helpers import (
    create_get_many_schema,
)
from middleware.schema_and_dto.schemas.locations.info.expanded import (
    LocationInfoExpandedSchema,
)

GetManyDataRequestsRelatedLocationsSchema = create_get_many_schema(
    data_list_schema=LocationInfoExpandedSchema,
    description="The list of locations associated with the data request",
)
