from endpoints.schema_config.helpers import schema_config_with_message_output
from middleware.primary_resource_logic.github_oauth import LinkToGithubRequestDTO
from middleware.schema_and_dto.schemas.auth.github.link import LinkToGithubRequestSchema

AuthGithubLinkEndpointSchemaConfig = schema_config_with_message_output(
    input_schema=LinkToGithubRequestSchema(),
    input_dto_class=LinkToGithubRequestDTO,
)
