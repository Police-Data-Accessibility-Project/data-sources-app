from typing import Optional

from db.constants import PAGE_SIZE


def get_offset(page: int) -> Optional[int]:
    if page is None:
        return None
    return (page - 1) * PAGE_SIZE
