from endpoints.instantiations.agencies_.post.dto import AgencyInfoPostDTO
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    pydantic_to_marshmallow,
)

AgencyInfoPostSchema = pydantic_to_marshmallow(AgencyInfoPostDTO)
