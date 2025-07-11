from endpoints.schema_config.config.core import EndpointSchemaConfig
from endpoints.instantiations.user.by_id.get.recent_searches.schema import GetUserRecentSearchesOuterSchema

UserProfileRecentSearchesEndpointSchemaConfig = EndpointSchemaConfig(
    primary_output_schema=GetUserRecentSearchesOuterSchema(exclude=["message"]),
)
