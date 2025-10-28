from typing import Sequence

from sqlalchemy import Select, RowMapping
from sqlalchemy.orm import Session

from db.models.base import Base


def mappings(session: Session, query: Select) -> Sequence[RowMapping]:
    raw_result = session.execute(query)
    return raw_result.mappings().all()


def add_many(
    session: Session, models: list[Base], return_ids: bool = False
) -> list[int] | None:
    session.add_all(models)
    if return_ids:
        if not hasattr(models[0], "id"):
            raise AttributeError("Models must have an id attribute")
        session.flush()
        return [
            model.id  # pyright: ignore [reportAttributeAccessIssue]
            for model in models
        ]
    return None
