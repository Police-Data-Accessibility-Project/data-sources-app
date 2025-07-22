from typing import Optional

from pydantic import BaseModel

from middleware.schema_and_dto.dtos._helpers import default_field_required
from utilities.enums import RecordCategoryEnum


class GetUserRecentSearchesDTO(BaseModel):
    state_name: str = default_field_required(
        description="The state name of the recent search."
    )
    county_name: Optional[str] = default_field_required(
        description="The county name of the recent search."
    )
    locality_name: Optional[str] = default_field_required(
        description="The locality name of the recent search."
    )
    location_type: str = default_field_required(
        description="The location type of the recent search."
    )
    location_id: int = default_field_required(
        description="The location id of the recent search."
    )
    record_categories: list[RecordCategoryEnum] = default_field_required(
        description="The record categories of the recent search."
    )
