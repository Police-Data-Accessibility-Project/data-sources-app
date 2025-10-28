from pydantic import BaseModel, Field

from middleware.enums import JurisdictionType, AgencyType


class UpdateAgenciesInnerRequest(BaseModel):
    app_id: int

    name: str = None
    jurisdiction_type: JurisdictionType | None = None
    agency_type: AgencyType | None = None
    location_ids: list[int] | None = Field(
        default=None,
        description="List of location IDs to be associated with the agency. " +
                    "If defined, fully overwrites previous associations.",
    )

    no_web_presence: bool = False
    defunct_year: int | None = None

class UpdateAgenciesOuterRequest(BaseModel):
    agencies: list[UpdateAgenciesInnerRequest] = Field(max_length=1000)