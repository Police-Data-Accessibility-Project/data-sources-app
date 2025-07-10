from endpoints.instantiations.user.by_id.patch.dto import UserPatchDTO
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import pydantic_to_marshmallow

UserPatchSchema = pydantic_to_marshmallow(UserPatchDTO)