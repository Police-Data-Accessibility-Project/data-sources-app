from endpoints.instantiations.search.core.models.response import SearchResponseDTO
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    pydantic_to_marshmallow,
)

SearchResponseSchema = pydantic_to_marshmallow(SearchResponseDTO)
