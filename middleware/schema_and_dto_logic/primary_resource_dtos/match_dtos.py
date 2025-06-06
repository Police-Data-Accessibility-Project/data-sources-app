from typing import Optional

from pydantic import BaseModel, Field

from db.enums import LocationType
from middleware.enums import AgencyType
from middleware.schema_and_dto_logic.primary_resource_dtos.helpers import (
    default_field_not_required,
    default_field_required,
)


class AgencyMatchRequestDTO(BaseModel):
    name: str = Field(
        description="The name of the agency to match.",
    )
    state: Optional[str] = default_field_not_required(
        "The state of the agency to match."
    )
    county: Optional[str] = default_field_not_required(
        description="The county of the agency to match.",
    )
    locality: Optional[str] = default_field_not_required(
        description="The locality of the agency to match.",
    )

    def has_location_data(self) -> bool:
        return (
            self.state is not None
            or self.county is not None
            or self.locality is not None
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
