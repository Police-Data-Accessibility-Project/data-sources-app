from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.schemas.user_profile.recent_searches import (
    GetUserRecentSearchesOuterSchema,
)

UserProfileRecentSearchesEndpointSchemaConfig = EndpointSchemaConfig(
    primary_output_schema=GetUserRecentSearchesOuterSchema(exclude=["message"]),
)
