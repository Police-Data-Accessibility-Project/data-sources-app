from typing import Optional

from pydantic import BaseModel

from db.enums import RequestUrgency, RequestStatus
from middleware.enums import RecordTypes


class DataRequestsPutDTO(BaseModel):
    title: str | None = None
    submission_notes: str | None = None
    request_urgency: RequestUrgency | None = None
    coverage_range: str | None = None
    data_requirements: str | None = None
    request_status: RequestStatus | None = None
    archive_reason: str | None = None
    github_issue_url: str | None = None
    github_issue_number: str | int | None = None
    internal_notes: str | None = None
    record_types_required: list[RecordTypes] | None = None
    pdap_response: str | None = None


class DataRequestsPutOuterDTO(BaseModel):
    entry_data: DataRequestsPutDTO
