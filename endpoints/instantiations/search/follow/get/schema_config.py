from endpoints.schema_config.config.core import EndpointSchemaConfig
from endpoints.instantiations.search._shared.schemas.follow import (
    GetUserFollowedSearchesSchema,
)

SearchFollowGetEndpointSchemaConfig = EndpointSchemaConfig(
    primary_output_schema=GetUserFollowedSearchesSchema(),
)
