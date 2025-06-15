from abc import ABC, abstractmethod
from typing import Any, Optional

from flask_sqlalchemy.session import Session
from sqlalchemy import Executable, Result, Select
from sqlalchemy.sql.compiler import SQLCompiler


class QueryBuilderBase(ABC):

    def __init__(self):
        self.session: Optional[Session] = None

    def build(self, session: Session) -> Any:
        self.session = session
        return self.run()

    @abstractmethod
    def run(self) -> Any: ...

    def execute(self, query: Executable) -> Result:
        return self.session.execute(query)

    def compile(self, query: Select) -> SQLCompiler:
        return query.compile(compile_kwargs={"literal_binds": True})
