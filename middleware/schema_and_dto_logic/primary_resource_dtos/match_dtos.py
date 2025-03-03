from typing import Optional

from pydantic import BaseModel

from database_client.enums import LocationType
from middleware.enums import AgencyType


class AgencyMatchRequestDTO(BaseModel):
    name: str
    state: Optional[str] = None
    county: Optional[str] = None
    locality: Optional[str] = None

    def has_location_data(self) -> bool:
        return (
            self.state is not None
            or self.county is not None
            or self.locality is not None
        )


class AgencyMatchResponseLocationDTO(BaseModel):
    state: Optional[str]
    county: Optional[str]
    locality: Optional[str]
    location_type: Optional[LocationType]


class AgencyMatchResponseInnerDTO(BaseModel):
    id: int
    name: str
    agency_type: AgencyType
    locations: list[AgencyMatchResponseLocationDTO]
    similarity: float


class AgencyMatchResponseOuterDTO(BaseModel):
    entries: list[AgencyMatchResponseInnerDTO]
