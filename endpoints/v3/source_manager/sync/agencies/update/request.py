from pydantic import BaseModel, Field

from endpoints.v3.source_manager.sync.agencies.shared.content import (
    AgencySyncContentModel,
)


class UpdateAgenciesInnerRequest(BaseModel):
    app_id: int
    content: AgencySyncContentModel


class UpdateAgenciesOuterRequest(BaseModel):
    agencies: list[UpdateAgenciesInnerRequest] = Field(max_length=1000)
