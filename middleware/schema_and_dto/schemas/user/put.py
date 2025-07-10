from middleware.schema_and_dto.dtos.user_profile import UserPutDTO
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    pydantic_to_marshmallow,
)

UserPutSchema = pydantic_to_marshmallow(UserPutDTO)
