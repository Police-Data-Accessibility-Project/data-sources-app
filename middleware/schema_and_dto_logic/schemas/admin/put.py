from middleware.schema_and_dto_logic.dtos.admin.put import AdminUserPutDTO
from middleware.schema_and_dto_logic.dynamic_logic.pydantic_to_marshmallow.core import (
    generate_marshmallow_schema,
)

AdminUsersPutSchema = generate_marshmallow_schema(AdminUserPutDTO)
