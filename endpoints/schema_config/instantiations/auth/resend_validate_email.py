from endpoints.schema_config.helpers import schema_config_with_message_output
from middleware.schema_and_dto.dtos.signup import EmailOnlyDTO
from middleware.schema_and_dto.schemas.signup import EmailOnlySchema

AuthResendValidationEmailEndpointSchemaConfig = schema_config_with_message_output(
    input_schema=EmailOnlySchema(),
    input_dto_class=EmailOnlyDTO,
)
