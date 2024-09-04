from dataclasses import dataclass
from typing import Optional

from database_client.enums import SortOrder


@dataclass
class OrderByParameters:
    """
    Contains parameters for an order_by clause
    """

    sort_by: str
    sort_order: SortOrder = SortOrder.ASCENDING

    @staticmethod
    def construct_from_args(sort_by: Optional[str], sort_order: Optional[SortOrder]) -> Optional["OrderByParameters"]:
        if sort_by is not None and sort_order is not None:
            return OrderByParameters(sort_by=sort_by, sort_order=sort_order)
        if sort_by is not None and sort_order is None:
            raise ValueError("If sort_by is provided, sort_order must also be provided")
        if sort_by is None and sort_order is not None:
            raise ValueError("If sort_order is provided, sort_by must also be provided")
        return None