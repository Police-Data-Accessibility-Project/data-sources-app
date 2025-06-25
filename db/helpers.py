from enum import Enum
from typing import Optional

from db.constants import PAGE_SIZE


def get_offset(page: int) -> int | None:
    """
    Calculates the offset value for pagination based on the given page number.
    Args:
        page (int): The page number for which the offset is to be calculated. Starts at 0.
    Returns:
        int: The calculated offset value.
    Example:
        >>> get_offset(3)
        2000
    """
    if page is None:
        return None
    return (page - 1) * PAGE_SIZE


def enum_value_or_none(e: Enum) -> str | int | None:
    try:
        return e.value
    except AttributeError:
        return None
