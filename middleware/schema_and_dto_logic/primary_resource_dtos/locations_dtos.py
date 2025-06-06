from typing import Optional

from pydantic import BaseModel, Field

from db.enums import LocationType


class LocationPutDTO(BaseModel):
    latitude: Optional[float] = Field(
        default=None,
        description="The latitude of the location",
    )
    longitude: Optional[float] = Field(
        default=None,
        description="The longitude of the location",
    )


class LatLngDTO(BaseModel):
    lat: Optional[float] = Field(
        default=None,
        description="The latitude of the location",
        json_schema_extra={"required": True},
    )
    lng: Optional[float] = Field(
        default=None,
        description="The longitude of the location",
        json_schema_extra={"required": True},
    )


class LocationsGetRequestDTO(BaseModel):
    page: int = 1
    type: Optional[LocationType] = None
    has_coordinates: Optional[bool] = None
