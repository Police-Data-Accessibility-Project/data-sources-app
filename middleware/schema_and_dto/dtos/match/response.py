from typing import Optional

from pydantic import BaseModel

from db.enums import LocationType
from middleware.enums import AgencyType
from middleware.schema_and_dto.dtos._helpers import (
    default_field_not_required,
    default_field_required,
)


class AgencyMatchResponseLocationDTO(BaseModel):
    state: Optional[str] = default_field_not_required(
        description="The state of the agency.",
    )
    county: Optional[str] = default_field_not_required(
        description="The county of the agency.",
    )
    locality: Optional[str] = default_field_not_required(
        description="The locality of the agency.",
    )
    location_type: Optional[LocationType] = default_field_not_required(
        description="The location type of the agency.",
    )


class AgencyMatchResponseInnerDTO(BaseModel):
    id: int = default_field_required(
        description="The id of the agency.",
    )
    name: str = default_field_required(
        description="The name of the agency.",
    )
    agency_type: AgencyType = default_field_required(
        description="The type of the agency.",
    )
    locations: list[AgencyMatchResponseLocationDTO] = default_field_required(
        description="The locations of the agency.",
    )
    similarity: float = default_field_required(
        description="The similarity of the agency to the search.",
    )


class AgencyMatchResponseOuterDTO(BaseModel):
    entries: list[AgencyMatchResponseInnerDTO]
