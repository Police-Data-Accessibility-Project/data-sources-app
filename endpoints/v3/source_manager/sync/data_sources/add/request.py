from datetime import date

from pydantic import BaseModel, Field, model_validator

from db.enums import (
    AgencyAggregation,
    UpdateMethod,
    RetentionSchedule,
    AccessType,
    DetailLevel,
    URLStatus,
)
from endpoints.v3.source_manager.sync.data_sources.shared.content import DataSourceSyncContentModel
from middleware.enums import RecordTypesEnum


class AddDataSourcesInnerRequest(BaseModel):
    request_id: int
    content: DataSourceSyncContentModel


class AddDataSourcesOuterRequest(BaseModel):
    data_sources: list[AddDataSourcesInnerRequest] = Field(max_length=1000)

    @model_validator(mode="after")
    def all_request_ids_unique(self):
        if len(self.data_sources) != len(
            set([data_source.request_id for data_source in self.data_sources])
        ):
            raise ValueError("All request_ids must be unique")
        return self
