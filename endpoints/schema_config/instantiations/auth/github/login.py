from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.dtos.github.login import LoginWithGithubRequestDTO
from middleware.schema_and_dto.schemas.auth.github.login import GithubRequestSchema
from middleware.schema_and_dto.schemas.auth.login import LoginResponseSchema

AuthGithubLoginEndpointSchemaConfig = EndpointSchemaConfig(
    input_schema=GithubRequestSchema(),
    input_dto_class=LoginWithGithubRequestDTO,
    primary_output_schema=LoginResponseSchema(),
)
