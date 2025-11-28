from typing import Sequence, Any

from sqlalchemy import Select, RowMapping
from sqlalchemy.orm import Session

from db.models.base import Base


def mappings(session: Session, query: Select) -> Sequence[RowMapping]:
    raw_result = session.execute(query)
    return raw_result.mappings().all()


def scalar(session: Session, query: Select) -> Any:
    raw_result = session.execute(query)
    return raw_result.scalar()


def results_exists(session: Session, query: Select) -> bool:
    raw_result = session.execute(query)
    return raw_result.scalar() is not None


def add(session: Session, model: Base, return_id: bool = False) -> int | None:
    session.add(model)
    if not return_id:
        return None
    if not hasattr(model, "id"):
        raise AttributeError("Model must have an id attribute")

    session.flush()
    return model.id


def add_many(
    session: Session, models: list[Base], return_ids: bool = False
) -> list[int] | None:
    if len(models) == 0:
        # nothing to add
        return [] if return_ids else None

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
