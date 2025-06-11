from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.schemas.search.follow import (
    GetUserFollowedSearchesSchema,
)

SearchFollowGetEndpointSchemaConfig = EndpointSchemaConfig(
    primary_output_schema=GetUserFollowedSearchesSchema(),
)
