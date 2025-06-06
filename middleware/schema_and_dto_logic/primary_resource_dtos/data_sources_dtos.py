from dataclasses import dataclass
from datetime import date
from typing import Optional, List

from pydantic import BaseModel, Field

from db.enums import (
    ApprovalStatus,
    AgencyAggregation,
    DetailLevel,
    AccessType,
    RetentionSchedule,
    URLStatus,
    UpdateMethod,
)
from middleware.enums import RecordTypes
from middleware.schema_and_dto_logic.dynamic_logic.pydantic_to_marshmallow.core import (
    MetadataInfo,
)


class DataSourceEntryBaseDTO(BaseModel):
    name: str = Field(
        description="The name of the data source concatenated with the state iso.",
    )
    description: Optional[str] = Field(
        description="Information to give clarity and confidence about what this source is, how it was "
        "processed, and whether the person reading the description might want to use it. "
        "Especially important if the source is difficult to preview or categorize.",
        default=None,
        json_schema_extra=MetadataInfo(required=False),
    )
    approval_status: Optional[ApprovalStatus] = Field(
        description="The approval status of the data source. Editable only by admins.",
        default=None,
        json_schema_extra=MetadataInfo(required=False),
    )
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
    update_method: Optional[UpdateMethod] = None
    tags: Optional[List[str]] = None
    readme_url: Optional[str] = None
    originating_entity: Optional[str] = None
    retention_schedule: Optional[RetentionSchedule] = None
    scraper_url: Optional[str] = None
    submitter_contact_info: Optional[str] = None
    submission_notes: Optional[str] = None
    agency_described_not_in_database: Optional[str] = None
    data_portal_type_other: Optional[str] = None
    access_notes: Optional[str] = None
    url_status: Optional[URLStatus] = None
    record_type_name: Optional[RecordTypes] = None


class DataSourceEntryDataPostDTO(DataSourceEntryBaseDTO):
    rejection_note: Optional[str] = None
    last_approval_editor: Optional[str] = None
    data_source_request: Optional[str] = None
    broken_source_url_as_of: Optional[date] = None


class DataSourceEntryDataPutDTO(DataSourceEntryBaseDTO): ...


class DataSourcesPutDTO(BaseModel):
    entry_data: DataSourceEntryDataPutDTO


class DataSourcesPostDTO(BaseModel):
    entry_data: DataSourceEntryDataPostDTO
    linked_agency_ids: Optional[List[int]] = None


class DataSourcesRejectDTO(BaseModel):
    resource_id: int
    rejection_note: str
