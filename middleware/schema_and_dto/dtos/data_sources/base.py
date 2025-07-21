from datetime import date

from pydantic import BaseModel, Field

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
from middleware.schema_and_dto.dtos._helpers import (
    default_field_required,
    default_field_not_required,
)
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.generator.models.metadata import (
    MetadataInfo,
)


class DataSourceEntryBaseDTO(BaseModel):
    name: str = default_field_required(
        description="The name of the data source concatenated with the state iso.",
    )
    description: str | None = default_field_not_required(
        description="Information to give clarity and confidence about what this source is, how it was "
        "processed, and whether the person reading the description might want to use it. "
        "Especially important if the source is difficult to preview or categorize.",
    )
    approval_status: ApprovalStatus = Field(
        default=ApprovalStatus.PENDING,
        description=description,
        json_schema_extra=MetadataInfo(required=False),
    )
    source_url: str | None = default_field_not_required(
        description="The URL of the data source.",
    )
    agency_supplied: bool | None = default_field_not_required(
        description='Is the relevant Agency also the entity supplying the data? This may be "no" if the Agency or local '
        "government contracted with a third party to publish this data, or if a third party was the original "
        "record-keeper."
    )
    supplying_entity: str | None = default_field_not_required(
        description="The name of the entity that supplied the data source, if not the agency itself.",
    )
    agency_originated: bool | None = default_field_not_required(
        description="Is the relevant Agency the entity that originally published this data source?"
        'This is usually "yes", unless a third party collected data about a police Agency.',
    )
    agency_aggregation: AgencyAggregation | None = default_field_not_required(
        description="If present, the Data Source describes multiple agencies."
    )
    coverage_start: date | None = None
    coverage_end: date | None = None
    detail_level: DetailLevel | None = None
    access_types: list[AccessType] = []
    data_portal_type: str | None = None
    record_formats: list[str] = []
    update_method: UpdateMethod | None = None
    tags: list[str] = []
    readme_url: str | None = None
    originating_entity: str | None = None
    retention_schedule: RetentionSchedule | None = None
    scraper_url: str | None = None
    submitter_contact_info: str | None = None
    submission_notes: str | None = None
    agency_described_not_in_database: str | None = None
    data_portal_type_other: str | None = None
    access_notes: str | None = None
    url_status: URLStatus | None = None
    record_type_name: RecordTypes | None = None
