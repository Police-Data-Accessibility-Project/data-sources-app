from middleware.schema_and_dto.dtos.locations.lat_lng import LatLngDTO
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    pydantic_to_marshmallow,
)

LatLngSchema = pydantic_to_marshmallow(LatLngDTO)
