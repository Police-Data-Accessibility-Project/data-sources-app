from typing import Optional

from pydantic import BaseModel


class AgencyMatchInnerDTO(BaseModel):
    name: str
    state: str
    county: Optional[str]
    locality: Optional[str]


class AgencyMatchOuterDTO(BaseModel):
    entries: list[AgencyMatchInnerDTO]
