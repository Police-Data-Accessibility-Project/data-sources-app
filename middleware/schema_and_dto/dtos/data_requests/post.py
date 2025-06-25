from typing import Optional

from pydantic import BaseModel

from db.enums import RequestUrgency


class RequestInfoPostDTO(BaseModel):
    title: str
    submission_notes: str
    request_urgency: RequestUrgency
    coverage_range: str | None = None
    data_requirements: str | None = None


class DataRequestsPostDTO(BaseModel):
    request_info: RequestInfoPostDTO
    location_ids: list[int] | None = None
