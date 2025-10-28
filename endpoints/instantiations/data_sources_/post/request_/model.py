from datetime import date
from typing import Optional

from pydantic import BaseModel

from db.enums import DetailLevel, AgencyAggregation, UpdateMethod, RetentionSchedule, AccessType, URLStatus
from middleware.enums import RecordTypesEnum
from middleware.schema_and_dto.dtos._helpers import default_field_not_required, default_field_required


class PostDataSourceRequest(BaseModel):
    # Required
    name: str = default_field_required()
    description: Optional[str] = default_field_not_required()
    source_url: str = default_field_required()
    agency_supplied: Optional[bool] = default_field_not_required()
    supplying_entity: Optional[str] = default_field_not_required()
    agency_originated: Optional[bool] = default_field_not_required()
    agency_aggregation: Optional[AgencyAggregation] = default_field_not_required()
    coverage_start: Optional[date] = default_field_not_required()
    coverage_end: Optional[date] = default_field_not_required()
    detail_level: Optional[DetailLevel] = default_field_not_required()
    access_types: Optional[list[AccessType]] = default_field_not_required()
    access_notes: Optional[str] = default_field_not_required()
    data_portal_type: Optional[str] = default_field_not_required()
    record_formats: Optional[list[str]] = default_field_not_required()
    update_method: Optional[UpdateMethod] = default_field_not_required()
    tags: Optional[list[str]] = default_field_not_required()
    readme_url: Optional[str] = default_field_not_required()
    originating_entity: Optional[str] = default_field_not_required()
    retention_schedule: Optional[RetentionSchedule] = default_field_not_required()
    scraper_url: Optional[str] = default_field_not_required()
    submission_notes: Optional[str] = default_field_not_required()  #X
    rejection_note: Optional[str] = default_field_not_required()  #X
    submitter_contact_info: Optional[str] = default_field_not_required()  #X
    agency_described_not_in_database: Optional[str] = default_field_not_required()
    data_portal_type_other: Optional[str] = default_field_not_required()
    data_source_request: Optional[str] = default_field_not_required()  #X
    record_type_name: RecordTypesEnum  = default_field_required()


    linked_agency_ids: list[int] = default_field_required()

class PostDataSourceOuterRequest(BaseModel):
    entry_data: PostDataSourceRequest = default_field_required()