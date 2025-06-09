from datetime import date
from typing import Optional, List

from pydantic import BaseModel

from db.enums import (
    ApprovalStatus,
    AgencyAggregation,
    DetailLevel,
    AccessType,
    UpdateMethod,
    RetentionSchedule,
    URLStatus,
)
from middleware.enums import RecordTypes
from middleware.schema_and_dto_logic.dtos._helpers import (
    default_field_required,
    default_field_not_required,
)


class DataSourceEntryBaseDTO(BaseModel):
    name: str = default_field_required(
        description="The name of the data source concatenated with the state iso.",
    )
    description: Optional[str] = default_field_not_required(
        description="Information to give clarity and confidence about what this source is, how it was "
        "processed, and whether the person reading the description might want to use it. "
        "Especially important if the source is difficult to preview or categorize.",
    )
    approval_status: Optional[ApprovalStatus] = default_field_not_required(
        description="The approval status of the data source. Editable only by admins.",
    )
    source_url: Optional[str] = default_field_not_required(
        description="The URL of the data source.",
    )
    agency_supplied: Optional[bool] = default_field_not_required(
        description='Is the relevant Agency also the entity supplying the data? This may be "no" if the Agency or local '
        "government contracted with a third party to publish this data, or if a third party was the original "
        "record-keeper."
    )
    supplying_entity: Optional[str] = default_field_not_required(
        description="The name of the entity that supplied the data source, if not the agency itself.",
    )
    agency_originated: Optional[bool] = default_field_not_required(
        description="Is the relevant Agency the entity that originally published this data source?"
        'This is usually "yes", unless a third party collected data about a police Agency.',
    )
    agency_aggregation: Optional[AgencyAggregation] = default_field_not_required(
        description="If present, the Data Source describes multiple agencies."
    )
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
