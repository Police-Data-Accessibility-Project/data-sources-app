from middleware.schema_and_dto.dtos.admin.put import AdminUserPutDTO
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    generate_marshmallow_schema,
)

AdminUsersPutSchema = generate_marshmallow_schema(AdminUserPutDTO)
