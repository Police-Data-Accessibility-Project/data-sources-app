from endpoints.instantiations.search.core.models.request import SearchRequestDTO
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    pydantic_to_marshmallow,
)

SearchRequestSchema = pydantic_to_marshmallow(SearchRequestDTO)
