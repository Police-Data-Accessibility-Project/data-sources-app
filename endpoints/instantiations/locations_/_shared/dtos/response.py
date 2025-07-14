from typing import Optional

from pydantic import BaseModel

from db.enums import LocationType
from middleware.schema_and_dto.dtos._helpers import default_field_required


class LocationInfoResponseDTO(BaseModel):
    type: LocationType = default_field_required(description="The type of location.")
    state_name: Optional[str] = default_field_required(
        description="The state name of the location."
    )
    state_iso: Optional[str] = default_field_required(
        description="The state iso of the location."
    )
    county_name: Optional[str] = default_field_required(
        description="The county name of the location."
    )
    county_fips: Optional[str] = default_field_required(
        description="The county fips of the location."
    )
    locality_name: Optional[str] = default_field_required(
        description="The locality name of the location."
    )
    display_name: str = default_field_required(
        description="The display name of the location."
    )
    location_id: int = default_field_required(
        description="The location id of the location."
    )
