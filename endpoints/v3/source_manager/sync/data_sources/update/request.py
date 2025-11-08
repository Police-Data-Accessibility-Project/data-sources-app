
from pydantic import BaseModel, Field

from endpoints.v3.source_manager.sync.data_sources.shared.content import (
    DataSourceSyncContentModel,
)


class UpdateDataSourcesInnerRequest(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    app_id: int
    content: DataSourceSyncContentModel


class UpdateDataSourcesOuterRequest(BaseModel):
    data_sources: list[UpdateDataSourcesInnerRequest] = Field(max_length=1000)
