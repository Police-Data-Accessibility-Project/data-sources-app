from middleware.schema_and_dto_logic.dtos.user_profile import UserPutDTO
from middleware.schema_and_dto_logic.dynamic_logic.pydantic_to_marshmallow.core import (
    generate_marshmallow_schema,
)

UserPutSchema = generate_marshmallow_schema(UserPutDTO)
