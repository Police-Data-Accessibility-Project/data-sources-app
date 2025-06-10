from abc import ABC, abstractmethod
from typing import Any

from flask_sqlalchemy.session import Session


class QueryBuilderBase(ABC):

    @abstractmethod
    def run(self, session: Session) -> Any: ...
