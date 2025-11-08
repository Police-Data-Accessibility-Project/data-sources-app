from pydantic import BaseModel, Field, model_validator

from endpoints.v3.source_manager.sync.agencies.shared.content import AgencySyncContentModel
from middleware.enums import JurisdictionType, AgencyType


class AddAgenciesInnerRequest(BaseModel):
    request_id: int
    content: AgencySyncContentModel


class AddAgenciesOuterRequest(BaseModel):
    agencies: list[AddAgenciesInnerRequest] = Field(max_length=1000)

    @model_validator(mode="after")
    def all_request_ids_unique(self):
        if len(self.agencies) != len(
            set([agency.request_id for agency in self.agencies])
        ):
            raise ValueError("All request_ids must be unique")
        return self
