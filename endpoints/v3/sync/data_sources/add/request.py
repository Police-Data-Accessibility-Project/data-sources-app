from datetime import date

from pydantic import BaseModel, Field, model_validator

from db.enums import AgencyAggregation, UpdateMethod, RetentionSchedule, AccessType, DetailLevel, URLStatus
from middleware.enums import RecordTypesEnum


class AddDataSourcesInnerRequest(BaseModel):
    request_id: int

    # Required
    url: str
    name: str
    record_type: RecordTypesEnum

    # Optional
    description: str | None = None

    # Optional data source metadata
    record_formats: list[str] | None = None
    data_portal_type: str | None = None
    supplying_entity: str | None = None
    coverage_start: date | None = None
    coverage_end: date | None = None
    detail_level: DetailLevel | None = None
    agency_supplied: bool | None = None
    agency_originated: bool | None = None
    agency_aggregation: AgencyAggregation | None = None
    agency_described_not_in_database: str | None = None
    update_method: UpdateMethod | None = None
    readme_url: str | None = None
    originating_entity: str | None = None
    retention_schedule: RetentionSchedule | None = None
    scraper_url: str | None = None
    access_notes: str | None = None
    access_types: list[AccessType] | None = None
    data_portal_type_other: str | None = None
    url_status: URLStatus | None = None

    agency_ids: list[int] = Field(min_length=1)

class AddDataSourcesOuterRequest(BaseModel):
    data_sources: list[AddDataSourcesInnerRequest] = Field(max_length=1000)

    @model_validator(mode='after')
    def all_request_ids_unique(self):
        if len(self.data_sources) != len(set([data_source.request_id for data_source in self.data_sources])):
            raise ValueError("All request_ids must be unique")
        return self