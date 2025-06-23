from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.dtos.github.data_requests import (
    GithubDataRequestsIssuesPostDTO,
)
from middleware.schema_and_dto.schemas.github.data_requests.request import (
    GithubDataRequestsIssuesPostRequestSchema,
)
from middleware.schema_and_dto.schemas.github.data_requests.response import (
    GithubDataRequestsIssuesPostResponseSchema,
)

GitHubDataRequestsIssuesPostEndpointSchemaConfig = EndpointSchemaConfig(
    input_schema=GithubDataRequestsIssuesPostRequestSchema(),
    primary_output_schema=GithubDataRequestsIssuesPostResponseSchema(),
    input_dto_class=GithubDataRequestsIssuesPostDTO,
)
