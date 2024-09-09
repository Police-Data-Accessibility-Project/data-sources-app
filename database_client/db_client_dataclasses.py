from dataclasses import dataclass
from typing import Callable, Optional

from sqlalchemy.sql.expression import asc, desc

from database_client.constants import TABLE_REFERENCE
from database_client.enums import SortOrder


ORDER_BY_REFERENCE = {
    "ASC": lambda column: asc(column),
    "DESC": lambda column: desc(column)
}


@dataclass
class OrderByParameters:
    """
    Contains parameters for an order_by clause
    """

    relation: str
    sort_by: str
    sort_order: SortOrder = SortOrder.ASCENDING

    @staticmethod
    def construct_from_args(sort_by: Optional[str], sort_order: Optional[SortOrder], relation: str) -> Optional["OrderByParameters"]:
        if sort_by is not None and sort_order is not None:
            return OrderByParameters(sort_by=sort_by, sort_order=sort_order, relation=relation)
        if sort_by is not None and sort_order is None:
            raise ValueError("If sort_by is provided, sort_order must also be provided")
        if sort_by is None and sort_order is not None:
            raise ValueError("If sort_order is provided, sort_by must also be provided")
        return None
    
    def build_order_by_clause(self) -> Callable:
        """Creates an order by clause for SQLAlchemy queries.

        :return: Order by clause. Example: asc(DataSource.name)
        """
        relation_reference = TABLE_REFERENCE[self.relation]
        order_by_func = ORDER_BY_REFERENCE[self.sort_order.value]
        return order_by_func(getattr(relation_reference, self.sort_by))
