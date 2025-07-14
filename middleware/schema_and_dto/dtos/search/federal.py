from typing import Optional

from pydantic import BaseModel

from utilities.enums import RecordCategoryEnum


class FederalSearchRequestDTO(BaseModel):
    record_categories: Optional[list[RecordCategoryEnum]] = None
    page: Optional[int] = None
