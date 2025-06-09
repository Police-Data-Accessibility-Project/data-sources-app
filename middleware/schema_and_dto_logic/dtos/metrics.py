from typing import Optional

from pydantic import BaseModel

from db.enums import SortOrder


class MetricsFollowedSearchesBreakdownRequestDTO(BaseModel):
    page: int = 1
    sort_by: Optional[str] = None
    sort_order: SortOrder = SortOrder.DESCENDING
