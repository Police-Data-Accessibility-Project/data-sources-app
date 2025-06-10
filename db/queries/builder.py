from abc import ABC, abstractmethod
from typing import Any

from flask_sqlalchemy.session import Session
from sqlalchemy import Executable, Result


class QueryBuilderBase(ABC):

    def __init__(self, session: Session) -> None:
        self.session = session

    @abstractmethod
    def run(self) -> Any: ...

    def execute(self, query: Executable) -> Result:
        return self.session.execute(query)
