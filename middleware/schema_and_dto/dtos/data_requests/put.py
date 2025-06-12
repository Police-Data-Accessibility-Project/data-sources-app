from typing import Optional

from pydantic import BaseModel

from db.enums import RequestUrgency, RequestStatus
from middleware.enums import RecordTypes


class DataRequestsPutDTO(BaseModel):
    title: Optional[str] = None
    submission_notes: Optional[str] = None
    request_urgency: Optional[RequestUrgency] = None
    coverage_range: Optional[str] = None
    data_requirements: Optional[str] = None
    request_status: Optional[RequestStatus] = None
    archive_reason: Optional[str] = None
    github_issue_url: Optional[str] = None
    github_issue_number: Optional[int] = None
    internal_notes: Optional[str] = None
    record_types_required: Optional[list[RecordTypes]] = None
    pdap_response: Optional[str] = None


class DataRequestsPutOuterDTO(BaseModel):
    entry_data: DataRequestsPutDTO
