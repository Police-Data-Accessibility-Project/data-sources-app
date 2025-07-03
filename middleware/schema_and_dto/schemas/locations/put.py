from middleware.schema_and_dto.dtos.locations.put import LocationPutDTO
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    pydantic_to_marshmallow,
)

LocationPutSchema = pydantic_to_marshmallow(LocationPutDTO)
