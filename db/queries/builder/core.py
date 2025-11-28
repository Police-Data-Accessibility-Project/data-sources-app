from abc import ABC, abstractmethod
from typing import Any, Sequence

from sqlalchemy import Executable, Result, Select, RowMapping
from sqlalchemy.orm import Session
from sqlalchemy.sql.compiler import SQLCompiler
from db.helpers_ import session as sh
from db.models.base import Base


class QueryBuilderBase(ABC):
    def __init__(self):
        self._session: Session | None = None
        self.sh = sh

    @property
    def session(self) -> Session:
        if self._session is None:
            raise RuntimeError("Session is not initialized")
        return self._session

    def build(self, session: Session) -> Any:
        self._session = session
        return self.run()

    @abstractmethod
    def run(self) -> Any: ...

    def execute(self, query: Executable) -> Result:
        return self.session.execute(query)

    def bulk_update_mappings(self, model: type[Base], mappings: list[dict[str, Any]]):
        return self.session.bulk_update_mappings(model, mappings=mappings)

    @staticmethod
    def compile(query: Select) -> SQLCompiler:
        return query.compile(compile_kwargs={"literal_binds": True})

    # Passthroughs to session helper
    def scalar(self, query: Select) -> Any:
        return self.sh.scalar(self.session, query=query)

    def mappings(self, query: Select) -> Sequence[RowMapping]:
        return self.sh.mappings(self.session, query=query)

    def add_many(self, models: list[Base], return_ids: bool = False):
        return self.sh.add_many(self.session, models=models, return_ids=return_ids)
