from typing import Optional

from pydantic import BaseModel

from utilities.enums import RecordCategories


class FederalSearchRequestDTO(BaseModel):
    record_categories: Optional[list[RecordCategories]] = None
    page: Optional[int] = None
