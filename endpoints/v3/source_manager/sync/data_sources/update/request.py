from datetime import date

from pydantic import BaseModel, Field

from db.enums import (
    AgencyAggregation,
    UpdateMethod,
    RetentionSchedule,
    DetailLevel,
    URLStatus,
    AccessType,
)
from endpoints.v3.source_manager.sync.data_sources.shared.content import DataSourceSyncContentModel
from middleware.enums import RecordTypesEnum


class UpdateDataSourcesInnerRequest(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    app_id: int
    content: DataSourceSyncContentModel

class UpdateDataSourcesOuterRequest(BaseModel):
    data_sources: list[UpdateDataSourcesInnerRequest] = Field(max_length=1000)
