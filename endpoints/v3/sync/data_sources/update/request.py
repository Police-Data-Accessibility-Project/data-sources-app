from datetime import date

from pydantic import BaseModel, Field

from db.enums import AgencyAggregation, UpdateMethod, RetentionSchedule, DetailLevel, URLStatus, AccessType
from middleware.enums import RecordTypesEnum


class UpdateDataSourcesInnerRequest(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    app_id: int

    # Required
    source_url: str | None = None
    name: str | None = None
    record_type: RecordTypesEnum | None = None

    # Optional
    description: str | None = None

    # Optional data source metadata
    record_formats: list[str] | None = None
    data_portal_type: str | None = None
    supplying_entity: str | None = None
    coverage_start: date | None = None
    coverage_end: date | None = None
    agency_supplied: bool | None = None
    agency_originated: bool | None = None
    agency_aggregation: AgencyAggregation | None = None
    agency_described_not_in_database: str | None = None
    update_method: UpdateMethod | None = None
    readme_url: str | None = None
    originating_entity: str | None = None
    retention_schedule: RetentionSchedule | None = None
    scraper_url: str | None = None
    submission_notes: str | None = None
    access_notes: str | None = None
    access_types: list[AccessType] | None = None
    detail_level: DetailLevel | None = None
    data_portal_type_other: str | None = None
    url_status: URLStatus | None = None

    agency_ids: list[int] | None = Field(
        min_length=1,
        default=None,
        description="List of agency IDs to be associated with the data source. " +
                    "Fully overwrites previous associations if defined.",
    )

class UpdateDataSourcesOuterRequest(BaseModel):
    data_sources: list[UpdateDataSourcesInnerRequest] = Field(max_length=1000)