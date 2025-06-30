from datetime import date

from pydantic import BaseModel

from middleware.schema_and_dto.dtos.data_sources.base import (
    DataSourceEntryBaseDTO,
)


class DataSourceEntryDataPostDTO(DataSourceEntryBaseDTO):
    rejection_note: str | None = None
    last_approval_editor: str | None = None
    data_source_request: str | None = None
    broken_source_url_as_of: date | None = None


class DataSourcesPostDTO(BaseModel):
    entry_data: DataSourceEntryDataPostDTO
    linked_agency_ids: list[int] | None = None
