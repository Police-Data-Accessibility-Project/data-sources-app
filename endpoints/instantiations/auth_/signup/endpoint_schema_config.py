from endpoints.instantiations.auth_.signup.dto import UserStandardSignupRequestDTO
from endpoints.instantiations.auth_.signup.schema import UserStandardSignupRequestSchema
from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.schema_and_dto.schemas.common.common_response_schemas import MessageSchema

AuthSignupEndpointSchemaConfig = EndpointSchemaConfig(
    input_schema=UserStandardSignupRequestSchema(),
    input_dto_class=UserStandardSignupRequestDTO,
    primary_output_schema=MessageSchema(),
)
