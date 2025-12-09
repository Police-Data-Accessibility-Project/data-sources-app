from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from db.models.templates.standard import StandardBase
from middleware.enums import Relations


class LinkRecentSearchRecordCategories(StandardBase):
    __tablename__ = Relations.LINK_RECENT_SEARCH_RECORD_CATEGORIES.value

    recent_search_id: Mapped[int] = mapped_column(
        ForeignKey("public.recent_searches.id")
    )
    record_category_id: Mapped[int] = mapped_column(
        ForeignKey("public.record_categories.id")
    )
