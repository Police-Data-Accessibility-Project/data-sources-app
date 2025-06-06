from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from db.enums import UpdateFrequency


class ArchivesGetRequestDTO(BaseModel):
    page: int
    update_frequency: Optional[UpdateFrequency] = None
    last_archived_before: Optional[datetime] = None
