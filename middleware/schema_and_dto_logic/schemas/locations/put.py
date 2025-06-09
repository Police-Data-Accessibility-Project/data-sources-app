from middleware.schema_and_dto_logic.dtos.locations.put import LocationPutDTO
from middleware.schema_and_dto_logic.dynamic_logic.pydantic_to_marshmallow.core import (
    generate_marshmallow_schema,
)

LocationPutSchema = generate_marshmallow_schema(LocationPutDTO)
