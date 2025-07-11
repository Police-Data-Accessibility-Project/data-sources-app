from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field

from db.enums import AgencyAggregation, DetailLevel, AccessType, UpdateMethod, RetentionSchedule, ApprovalStatus, \
    URLStatus
from middleware.schema_and_dto.dtos._helpers import default_field_required, default_field_not_required
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.generator.models.metadata import MetadataInfo


class DataSourceBaseDTO(BaseModel):
    name: str = default_field_required(description="The name of the data source.")
    description: Optional[str] = Field(
        default="",
        description="Information to give clarity and confidence about what this source is, how it was " +
                    "processed, and whether the person reading the description might want to use it. " +
                    "Especially important if the source is difficult to preview or categorize.",
        json_schema_extra=MetadataInfo(required=False),
    )
    source_url: Optional[str] = default_field_required(
        description="The URL of the data source."
    )
    agency_supplied: Optional[bool] = default_field_not_required(
        description='Is the relevant Agency also the entity supplying the data? This may be "no" if the Agency or local ' +
                    "government contracted with a third party to publish this data, or if a third party was the original " +
                    "record-keeper."
    )
    supplying_entity: Optional[str] = default_field_not_required(
        description="The name of the entity that supplied the data source, if not the agency itself."
    )
    agency_originated: Optional[bool] = default_field_not_required(
        description="Is the relevant Agency the entity that originally published this data source? " +
                    'This is usually "yes", unless a third party collected data about a police Agency.'
    )
    agency_aggregation: Optional[AgencyAggregation] = default_field_not_required(
        description="If present, the aggregation level of the data source."
    )
    coverage_start: Optional[date] = default_field_not_required(
        description="Start date of the data source’s coverage."
    )
    coverage_end: Optional[date] = default_field_not_required(
        description="End date of the data source’s coverage."
    )
    updated_at: Optional[datetime] = default_field_not_required(
        description="The date and time the data source was last updated."
    )
    detail_level: Optional[DetailLevel] = default_field_not_required(
        description="The detail level of the data source."
    )
    access_types: Optional[list[AccessType]] = default_field_not_required(
        description="The ways the data source can be accessed. Editable only by admins."
    )
    data_portal_type: Optional[str] = default_field_not_required(
        description="The type of data portal. Editable only by admins."
    )
    record_formats: Optional[list[str]] = default_field_not_required(
        description="What formats the data source can be obtained in."
    )
    update_method: Optional[UpdateMethod] = default_field_not_required(
        description="The method used to update the data source."
    )
    tags: Optional[list[str]] = default_field_not_required(
        description="The tags associated with the data source."
    )
    readme_url: Optional[str] = default_field_not_required(
        description="A URL where supplementary information about the source is published."
    )
    originating_entity: Optional[str] = default_field_not_required(
        description="The entity that originally provided this data source."
    )
    retention_schedule: Optional[RetentionSchedule] = default_field_not_required(
        description="The retention schedule of the data source."
    )
    id: int = default_field_required(description="The ID of the data source.")
    scraper_url: Optional[str] = default_field_not_required(
        description="The URL of the data source's scraper."
    )
    created_at: datetime = default_field_not_required(
        description="The date and time the data source was created."
    )
    submission_notes: Optional[str] = default_field_not_required(
        description="Optional notes provided by the submitter during the request submission."
    )
    rejection_note: Optional[str] = default_field_not_required(
        description="Why the data source was rejected."
    )
    last_approval_editor: Optional[int] = default_field_not_required(
        description="The id of the user who last approved the data source."
    )
    submitter_contact_info: Optional[str] = default_field_not_required(
        description="The contact information of the submitter."
    )
    agency_described_not_in_database: Optional[str] = default_field_not_required(
        description="If the agency associated is not in the database, why?"
    )
    data_portal_type_other: Optional[str] = default_field_not_required(
        description="What unconventional data portal this data source is derived from"
    )
    data_source_request: Optional[str] = default_field_not_required(
        description="Airtable UID of the associated data source request"
    )
    broken_source_url_as_of: Optional[date] = default_field_not_required(
        description="Timestamp indicating when the source URL was reported as broken."
    )
    access_notes: Optional[str] = default_field_not_required(
        description="How to access the data source."
    )
    url_status: Optional[URLStatus] = default_field_not_required(
        description="Status of the source URL. Editable only by admins."
    )
    approval_status: ApprovalStatus = default_field_not_required(
        description="The approval status of the data source. Editable only by admins."
    )
    record_type_id: Optional[int] = default_field_not_required(
        description="The id of the record type for this data source."
    )
    approval_status_updated_at: datetime = default_field_not_required(
        description="The date and time the approval status was last updated."
    )
    last_approval_editor_old: Optional[str] = default_field_not_required(
        description="Former identifier of who provided approval for the data source."
    )