from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.dtos.github.oauth import GithubOAuthRequestDTO
from middleware.schema_and_dto.schemas.auth.github.oauth import GithubOAuthRequestSchema

AuthGitHubOAuthEndpointSchemaConfig = EndpointSchemaConfig(
    input_schema=GithubOAuthRequestSchema(),
    input_dto_class=GithubOAuthRequestDTO,
)
