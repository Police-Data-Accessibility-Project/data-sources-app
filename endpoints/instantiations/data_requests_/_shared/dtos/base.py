from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from db.enums import RequestStatus, RequestUrgency
from middleware.enums import RecordTypes
from middleware.schema_and_dto.dtos._helpers import default_field_required, default_field_not_required
from pydantic import Field

from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.generator.models.metadata import MetadataInfo


class DataRequestsBaseDTO(BaseModel):
    id: int = default_field_required(description="The id of the data request.")
    title: str = Field(
        description="The title of the data request.",
        json_schema_extra=MetadataInfo(),
        min_length=1,
        max_length=255
    )
    submission_notes: str = default_field_required(
        description="Optional notes provided by the submitter during the request submission."
    )
    request_status: RequestStatus = default_field_required(
        description="The status of the data request. Editable only by admins."
    )
    archive_reason: Optional[str] = default_field_not_required(
        description="If applicable, the reason for archiving the data request. Viewable only by owners and admins. Editable only by admins."
    )
    date_created: datetime = default_field_required(
        description="The date and time the data request was created."
    )
    date_status_last_changed: datetime = default_field_required(
        description="The date and time the data request status was last changed."
    )
    creator_user_id: int = default_field_not_required(
        description="The id of the user who created the data request."
    )
    github_issue_url: Optional[str] = default_field_required(
        description="The github issue url for the data request."
    )
    github_issue_number: Optional[int] = default_field_required(
        description="The github issue number for the data request."
    )
    internal_notes: Optional[str] = default_field_not_required(
        description="Internal notes by PDAP staff about the request. Viewable and editable only by admins."
    )
    record_types_required: Optional[list[RecordTypes]] = default_field_required(
        description="The record types associated with the data request. Editable only by admins."
    )
    pdap_response: Optional[str] = default_field_required(
        description="The PDAP response to the data request. Editable only by admins."
    )
    coverage_range: Optional[str] = default_field_not_required(
        description="The date_range covered by the request, if applicable."
    )
    data_requirements: Optional[str] = default_field_not_required(
        description="The data requirements of the request, if applicable."
    )
    request_urgency: RequestUrgency = default_field_required(
        description="The urgency of the request."
    )