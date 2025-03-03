import enum
from dataclasses import dataclass
from typing import Any, Callable, Optional

from pydantic import BaseModel
from sqlalchemy.sql.expression import UnaryExpression
from sqlalchemy.schema import Column
from sqlalchemy.sql.expression import asc, desc, BinaryExpression

from database_client.enums import SortOrder
from database_client.models import SQL_ALCHEMY_TABLE_REFERENCE


ORDER_BY_REFERENCE = {
    "ASC": lambda column: asc(column),
    "DESC": lambda column: desc(column),
}


class OrderByParameters(BaseModel):
    """
    Contains parameters for an order_by clause
    """

    sort_by: str
    sort_order: SortOrder = SortOrder.ASCENDING

    @staticmethod
    def construct_from_args(
        sort_by: Optional[str], sort_order: Optional[SortOrder]
    ) -> Optional["OrderByParameters"]:
        if sort_by is not None and sort_order is not None:
            return OrderByParameters(sort_by=sort_by, sort_order=sort_order)
        if sort_by is not None and sort_order is None:
            raise ValueError("If sort_by is provided, sort_order must also be provided")
        if sort_by is None:
            return None
        return None

    def build_order_by_clause(self, relation) -> Callable[[Column], UnaryExpression]:
        """Creates an order by clause for SQLAlchemy queries.

        :param relation:
        :return: Order by clause. Example: asc(DataSource.name)
        """
        relation_reference = SQL_ALCHEMY_TABLE_REFERENCE[relation]
        order_by_func = ORDER_BY_REFERENCE[self.sort_order.value]
        return order_by_func(getattr(relation_reference, self.sort_by))


@dataclass
class WhereMapping:
    """
    Contains parameters for a where clause
    """

    column: str
    value: Any
    eq: bool = True

    def build_where_clause(self, relation: str) -> BinaryExpression:
        """Creates a SQLAlchemy BinaryExpression for queries.

        :param relation:
        :return: BinaryExpression. Example: Agency.municipality == "Pittsburgh"
        """
        if isinstance(self.value, list):
            return self.build_where_clause_in_list(relation)
        relation_reference = SQL_ALCHEMY_TABLE_REFERENCE[relation]
        if self.eq is True:
            return getattr(relation_reference, self.column) == self.value
        elif self.eq is False:
            return getattr(relation_reference, self.column) != self.value

    def build_where_clause_in_list(self, relation: str) -> BinaryExpression:
        """Creates a SQLAlchemy BinaryExpression for queries.

        :param relation:
        :return: BinaryExpression. Example: Agency.municipality == "Pittsburgh"
        """
        relation_reference = SQL_ALCHEMY_TABLE_REFERENCE[relation]
        return getattr(relation_reference, self.column).in_(self.value)

    @staticmethod
    def from_dict(d: dict) -> list["WhereMapping"]:
        results = []
        for key, value in d.items():
            if isinstance(value, enum.Enum):
                value = value.value
            results.append(WhereMapping(column=key, value=value))
        return results
