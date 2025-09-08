from typing import Sequence

from sqlalchemy import Select, RowMapping
from sqlalchemy.orm import Session


def mappings(
    session: Session,
    query: Select
) -> Sequence[RowMapping]:
    raw_result = session.execute(query)
    return raw_result.mappings().all()