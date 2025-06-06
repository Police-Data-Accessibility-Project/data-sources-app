from typing import Optional

from pydantic import BaseModel

from db.enums import LocationType


class LocationPutDTO(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class LocationsGetRequestDTO(BaseModel):
    page: int = 1
    type: Optional[LocationType] = None
    has_coordinates: Optional[bool] = None
