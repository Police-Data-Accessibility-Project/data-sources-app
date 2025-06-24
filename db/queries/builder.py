from abc import ABC, abstractmethod
from typing import Any, Optional

from sqlalchemy import Executable, Result, Select
from sqlalchemy.orm import Session
from sqlalchemy.sql.compiler import SQLCompiler


class QueryBuilderBase(ABC):

    def __init__(self):
        self._session: Session | None = None

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

    @staticmethod
    def compile(query: Select) -> SQLCompiler:
        return query.compile(compile_kwargs={"literal_binds": True})
