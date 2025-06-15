from middleware.schema_and_dto.dtos.locations.put import LocationPutDTO
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    generate_marshmallow_schema,
)

LocationPutSchema = generate_marshmallow_schema(LocationPutDTO)
