from middleware.schema_and_dto.dtos.admin.put import AdminUserPutDTO
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    pydantic_to_marshmallow,
)

AdminUsersPutSchema = pydantic_to_marshmallow(AdminUserPutDTO)
