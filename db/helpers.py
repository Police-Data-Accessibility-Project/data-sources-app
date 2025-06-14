from typing import Optional

from db.constants import PAGE_SIZE


def get_offset(page: int) -> Optional[int]:
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
