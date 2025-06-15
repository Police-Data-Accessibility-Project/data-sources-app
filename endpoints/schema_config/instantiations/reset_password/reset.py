from endpoints.schema_config.helpers import schema_config_with_message_output
from middleware.schema_and_dto.dtos.reset_password.reset import ResetPasswordDTO
from middleware.schema_and_dto.schemas.reset_password.reset import ResetPasswordSchema

ResetPasswordEndpointSchemaConfig = schema_config_with_message_output(
    input_schema=ResetPasswordSchema(),
    input_dto_class=ResetPasswordDTO,
)
