from endpoints.instantiations.auth_.resend_validation_email.dto import EmailOnlyDTO
from endpoints.instantiations.auth_.resend_validation_email.schema import (
    EmailOnlySchema,
)
from endpoints.schema_config.helpers import schema_config_with_message_output

AuthResendValidationEmailEndpointSchemaConfig = schema_config_with_message_output(
    input_schema=EmailOnlySchema(),
    input_dto_class=EmailOnlyDTO,
)
