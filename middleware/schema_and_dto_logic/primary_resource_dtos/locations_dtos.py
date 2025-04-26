from typing import Optional

from pydantic import BaseModel

from database_client.enums import LocationType


class LocationPutDTO(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class LocationsGetRequestDTO(BaseModel):
    type: Optional[LocationType] = None
    has_coordinates: Optional[bool] = None
