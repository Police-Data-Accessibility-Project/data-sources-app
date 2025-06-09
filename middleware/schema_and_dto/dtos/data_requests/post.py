from typing import Optional

from pydantic import BaseModel

from db.db_client_dataclasses import WhereMapping
from db.enums import LocationType, RequestUrgency


class RequestInfoPostDTO(BaseModel):
    title: str
    submission_notes: str
    request_urgency: RequestUrgency
    coverage_range: Optional[str] = None
    data_requirements: Optional[str] = None


class DataRequestsPostDTO(BaseModel):
    request_info: RequestInfoPostDTO
    location_ids: Optional[list[int]] = None
