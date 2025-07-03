from middleware.schema_and_dto.dtos.signup import EmailOnlyDTO
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    pydantic_to_marshmallow,
)

EmailOnlySchema = pydantic_to_marshmallow(EmailOnlyDTO)
