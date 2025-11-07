from pydantic import BaseModel, Field

from db.enums import LocationType


class GetUserSearchLocationModel(BaseModel):
    state_name: str | None = Field(
        description="The state name of the recent search.",
    )
    county_name: str | None = Field(
        description="The county name of the recent search.",
    )
    locality_name: str | None = Field(
        description="The locality name of the recent search.",
    )
    location_type: LocationType | None = Field(
        description="The location type of the recent search.",
    )
    location_id: int | None = Field(
        description="The location ID of the recent search.",
    )