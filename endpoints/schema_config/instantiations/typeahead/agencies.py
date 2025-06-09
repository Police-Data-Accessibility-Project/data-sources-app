from endpoints.schema_config.helpers import get_typeahead_schema_config
from middleware.schema_and_dto.schemas.typeahead.agencies import (
    TypeaheadAgenciesOuterResponseSchema,
)

TypeaheadAgenciesEndpointSchemaConfig = get_typeahead_schema_config(
    primary_output_schema=TypeaheadAgenciesOuterResponseSchema(),
)
