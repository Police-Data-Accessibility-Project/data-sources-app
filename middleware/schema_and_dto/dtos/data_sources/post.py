from datetime import date
from typing import Optional, List

from pydantic import BaseModel

from middleware.schema_and_dto.dtos.data_sources.base import (
    DataSourceEntryBaseDTO,
)


class DataSourceEntryDataPostDTO(DataSourceEntryBaseDTO):
    rejection_note: Optional[str] = None
    last_approval_editor: Optional[str] = None
    data_source_request: Optional[str] = None
    broken_source_url_as_of: Optional[date] = None


class DataSourcesPostDTO(BaseModel):
    entry_data: DataSourceEntryDataPostDTO
    linked_agency_ids: Optional[List[int]] = None
