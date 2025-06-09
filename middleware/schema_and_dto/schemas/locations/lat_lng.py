from middleware.schema_and_dto.dtos.locations.lat_lng import LatLngDTO
from middleware.schema_and_dto.dynamic_logic.pydantic_to_marshmallow.core import (
    generate_marshmallow_schema,
)

LatLngSchema = generate_marshmallow_schema(LatLngDTO)
