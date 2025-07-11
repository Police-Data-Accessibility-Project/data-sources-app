from endpoints.instantiations.search._shared.dtos.follow import FollowSearchResponseDTO, GetUserFollowedSearchesDTO
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import pydantic_to_marshmallow

FollowSearchResponseSchema = pydantic_to_marshmallow(FollowSearchResponseDTO)

GetUserFollowedSearchesSchema = pydantic_to_marshmallow(
    GetUserFollowedSearchesDTO
)
