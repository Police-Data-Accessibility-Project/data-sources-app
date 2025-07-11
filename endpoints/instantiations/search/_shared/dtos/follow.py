from typing import Optional

from pydantic import BaseModel

from middleware.schema_and_dto.dtos._helpers import default_field_required, default_field_not_required
from middleware.schema_and_dto.dtos.dto_helpers import create_get_many_dto


class FollowSearchResponseDTO(BaseModel):
    state_name: Optional[str] = default_field_required(description="The state name of the search.")
    display_name: str = default_field_required(description="The display name of the search.")
    county_name: Optional[str] = default_field_not_required(
        description="The county name of the search. If empty, all counties for the given state will be searched.")
    locality_name: Optional[str] = default_field_not_required(
        description="The locality name of the search. If empty, all localities for the given county will be searched.")
    location_id: int = default_field_required(description="The location id of the search.")
    subscriptions_by_category: dict[str, str] = default_field_required(
        description="The record categories of the search."
    )

GetUserFollowedSearchesDTO = create_get_many_dto(
    data_list_dto=FollowSearchResponseDTO,
    description="The followed searches of the user."
)