from endpoints.schema_config.helpers import get_user_request_endpoint_schema_config
from middleware.schema_and_dto.schemas.common.common_response_schemas import (
    MessageSchema,
)

AuthSignupEndpointSchemaConfig = get_user_request_endpoint_schema_config(
    primary_output_schema=MessageSchema(),
)
