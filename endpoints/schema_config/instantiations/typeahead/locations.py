from endpoints.schema_config.helpers import get_typeahead_schema_config
from middleware.schema_and_dto.schemas.typeahead.locations import (
    TypeaheadLocationsOuterResponseSchema,
)

TypeaheadLocationsEndpointSchemaConfig = get_typeahead_schema_config(
    primary_output_schema=TypeaheadLocationsOuterResponseSchema(),
)
