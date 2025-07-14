from endpoints.instantiations.locations_._shared.dtos.response import (
    LocationInfoResponseDTO,
)
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    pydantic_to_marshmallow,
)

LocationInfoResponseSchema = pydantic_to_marshmallow(LocationInfoResponseDTO)
