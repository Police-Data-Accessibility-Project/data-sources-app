from endpoints.instantiations.user.by_id.get.recent_searches.dto import (
    GetUserRecentSearchesOuterDTO,
)
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    pydantic_to_marshmallow,
)

GetUserRecentSearchesOuterSchema = pydantic_to_marshmallow(
    GetUserRecentSearchesOuterDTO
)
