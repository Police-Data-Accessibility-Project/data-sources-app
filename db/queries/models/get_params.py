from typing import Optional

from pydantic import BaseModel

from db.constants import PAGE_SIZE
from db.db_client_dataclasses import OrderByParameters


class GetParams(BaseModel):

    class Config:
        arbitrary_types_allowed = True

    order_by: Optional[OrderByParameters] = (None,)
    page: Optional[int] = (1,)
    limit: Optional[int] = (PAGE_SIZE,)
    requested_columns: Optional[list[str]] = (None,)
