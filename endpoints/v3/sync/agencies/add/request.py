from pydantic import BaseModel, Field, model_validator

from middleware.enums import JurisdictionType, AgencyType


class AddAgenciesInnerRequest(BaseModel):
    request_id: int

    # Required
    name: str
    jurisdiction_type: JurisdictionType
    agency_type: AgencyType
    location_ids: list[int] = Field(min_length=1)

    # Optional
    no_web_presence: bool = False
    defunct_year: int | None = None


class AddAgenciesOuterRequest(BaseModel):
    agencies: list[AddAgenciesInnerRequest] = Field(max_length=1000)

    @model_validator(mode="after")
    def all_request_ids_unique(self):
        if len(self.agencies) != len(
            set([agency.request_id for agency in self.agencies])
        ):
            raise ValueError("All request_ids must be unique")
        return self
