from typing import Optional

from pydantic import BaseModel, Field

from db.enums import LocationType
from middleware.schema_and_dto_logic.dynamic_logic.pydantic_to_marshmallow.core import (
    MetadataInfo,
)


class LocationPutDTO(BaseModel):
    latitude: Optional[float] = Field(
        default=None,
        description="The latitude of the location",
        json_schema_extra=MetadataInfo(required=False),
    )
    longitude: Optional[float] = Field(
        default=None,
        description="The longitude of the location",
        json_schema_extra=MetadataInfo(required=False),
    )


class LatLngDTO(BaseModel):
    lat: Optional[float] = Field(
        default=None,
        description="The latitude of the location",
        json_schema_extra=MetadataInfo(required=False),
    )
    lng: Optional[float] = Field(
        default=None,
        description="The longitude of the location",
        json_schema_extra=MetadataInfo(required=False),
    )


class LocationsGetRequestDTO(BaseModel):
    page: int = 1
    type: Optional[LocationType] = None
    has_coordinates: Optional[bool] = None
