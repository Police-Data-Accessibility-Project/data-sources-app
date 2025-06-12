from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.dtos.search.national import (
    SearchFollowNationalRequestDTO,
)
from middleware.schema_and_dto.schemas.common.common_response_schemas import (
    MessageSchema,
)

from middleware.schema_and_dto.schemas.search.request import SearchRequestSchema

SearchFollowNationalEndpointSchemaConfig = EndpointSchemaConfig(
    input_schema=SearchRequestSchema(
        exclude=["output_format", "location_id"],
    ),
    primary_output_schema=MessageSchema(),
    input_dto_class=SearchFollowNationalRequestDTO,
)
