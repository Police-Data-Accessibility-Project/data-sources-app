from endpoints.instantiations.auth_.signup.dto import UserStandardSignupRequestDTO
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    pydantic_to_marshmallow,
)

UserStandardSignupRequestSchema = pydantic_to_marshmallow(UserStandardSignupRequestDTO)
