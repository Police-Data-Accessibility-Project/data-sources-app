from pydantic import BaseModel

from middleware.enums import RecordTypes


class SourceCollectorPostRequestInnerDTO(BaseModel):
    name: str
    description: str | None = None
    source_url: str
    record_type: RecordTypes
    record_formats: list[str] | None = None
    data_portal_type: str | None = None
    last_approval_editor: int
    supplying_entity: str | None = None
    agency_ids: list[int]


class SourceCollectorPostRequestDTO(BaseModel):
    data_sources: list[SourceCollectorPostRequestInnerDTO]
