from endpoints.schema_config.helpers import get_user_request_endpoint_schema_config
from middleware.schema_and_dto.schemas.auth.login import LoginResponseSchema

LoginEndpointSchemaConfig = get_user_request_endpoint_schema_config(
    primary_output_schema=LoginResponseSchema(),
)
