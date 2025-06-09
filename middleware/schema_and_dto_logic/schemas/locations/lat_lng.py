from middleware.schema_and_dto_logic.dtos.locations.lat_lng import LatLngDTO
from middleware.schema_and_dto_logic.dynamic_logic.pydantic_to_marshmallow.core import (
    generate_marshmallow_schema,
)

LatLngSchema = generate_marshmallow_schema(LatLngDTO)
