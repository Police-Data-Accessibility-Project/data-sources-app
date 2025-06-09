from typing import Optional

from pydantic import BaseModel

from db.enums import LocationType


class LocationInfoDTO(BaseModel):
    type: LocationType
    state_iso: str
    county_fips: Optional[str] = None
    locality_name: Optional[str] = None
