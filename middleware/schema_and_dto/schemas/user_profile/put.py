from middleware.schema_and_dto.dtos.user_profile import UserPutDTO
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    generate_marshmallow_schema,
)

UserPutSchema = generate_marshmallow_schema(UserPutDTO)
