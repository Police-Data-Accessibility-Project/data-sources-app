from typing import Optional

from pydantic import BaseModel

from middleware.enums import RecordTypes, DataSourceCreationResponse


class SourceCollectorPostRequestInnerDTO(BaseModel):
    name: str
    description: Optional[str] = None
    source_url: str
    record_type: RecordTypes
    record_formats: Optional[list[str]] = None
    data_portal_type: Optional[str] = None
    last_approval_editor: int
    supplying_entity: Optional[str] = None
    agency_ids: list[int]


class SourceCollectorPostRequestDTO(BaseModel):
    data_sources: list[SourceCollectorPostRequestInnerDTO]


class SourceCollectorPostResponseInnerDTO(BaseModel):
    url: str
    status: DataSourceCreationResponse
    data_source_id: Optional[int] = None
    error: Optional[str] = None
