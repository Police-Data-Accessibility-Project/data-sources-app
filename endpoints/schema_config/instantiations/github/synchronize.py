from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.schemas.github.synchronize import (
    GithubSynchronizeResponseSchema,
)

GitHubDataRequestsSynchronizePostEndpointSchemaConfig = EndpointSchemaConfig(
    primary_output_schema=GithubSynchronizeResponseSchema(),
)
