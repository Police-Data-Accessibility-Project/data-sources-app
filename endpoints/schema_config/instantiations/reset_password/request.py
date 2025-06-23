from endpoints.schema_config.helpers import schema_config_with_message_output
from middleware.schema_and_dto.dtos.reset_password.request import (
    RequestResetPasswordRequestDTO,
)
from middleware.schema_and_dto.schemas.reset_password.request import (
    RequestResetPasswordRequestSchema,
)

RequestResetPasswordEndpointSchemaConfig = schema_config_with_message_output(
    input_schema=RequestResetPasswordRequestSchema(),
    input_dto_class=RequestResetPasswordRequestDTO,
)
