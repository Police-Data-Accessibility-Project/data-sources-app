from sqlalchemy.orm import relationship

from db.models.mixins import CreatedAtMixin, UserIDMixin, LocationIDMixin
from db.models.templates.standard import StandardBase
from middleware.enums import Relations


class RecentSearch(StandardBase, CreatedAtMixin, UserIDMixin, LocationIDMixin):
    __tablename__ = Relations.RECENT_SEARCHES.value

    record_categories = relationship(
        "RecordCategory",
        secondary="public.link_recent_search_record_categories",
        primaryjoin="RecentSearch.id == LinkRecentSearchRecordCategories.recent_search_id",
        secondaryjoin="LinkRecentSearchRecordCategories.record_category_id == RecordCategory.id",
    )
