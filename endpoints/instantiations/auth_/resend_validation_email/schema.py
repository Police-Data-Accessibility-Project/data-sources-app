from endpoints.instantiations.auth_.resend_validation_email.dto import EmailOnlyDTO
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    pydantic_to_marshmallow,
)

EmailOnlySchema = pydantic_to_marshmallow(EmailOnlyDTO)
