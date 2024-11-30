from dataclasses import dataclass
from datetime import date
from typing import Optional, List

from pydantic import BaseModel

from database_client.enums import (
    ApprovalStatus,
    AgencyAggregation,
    DetailLevel,
    AccessType,
    RetentionSchedule,
    URLStatus,
)
from middleware.enums import RecordType


class DataSourceEntryDataPostDTO(BaseModel):
    submitted_name: str
    description: Optional[str] = None
    approval_status: Optional[ApprovalStatus] = None
    source_url: Optional[str] = None
    agency_supplied: Optional[bool] = None
    supplying_entity: Optional[str] = None
    agency_originated: Optional[bool] = None
    agency_aggregation: Optional[AgencyAggregation] = None
    coverage_start: Optional[date] = None
    coverage_end: Optional[date] = None
    detail_level: Optional[DetailLevel] = None
    access_types: Optional[List[AccessType]] = None
    data_portal_type: Optional[str] = None
    record_formats: Optional[List[str]] = None
    update_method: Optional[str] = None
    tags: Optional[List[str]] = None
    readme_url: Optional[str] = None
    originating_entity: Optional[str] = None
    retention_schedule: Optional[RetentionSchedule] = None
    scraper_url: Optional[str] = None
    submission_notes: Optional[str] = None
    rejection_note: Optional[str] = None
    last_approval_editor: Optional[str] = None
    submitter_contact_info: Optional[str] = None
    agency_described_submitted: Optional[str] = None
    agency_described_not_in_database: Optional[str] = None
    data_portal_type_other: Optional[str] = None
    data_source_request: Optional[str] = None
    broken_source_url_as_of: Optional[date] = None
    access_notes: Optional[str] = None
    url_status: Optional[URLStatus] = None
    record_type_name: Optional[RecordType] = None


@dataclass
class DataSourcesPostDTO:
    entry_data: DataSourceEntryDataPostDTO
    linked_agency_ids: Optional[List[int]] = None
