from db.models.mixins import CreatedAtMixin, UserIDMixin, LocationIDMixin
from db.models.templates.standard import StandardBase
from middleware.enums import Relations


class RecentSearch(StandardBase, CreatedAtMixin, UserIDMixin, LocationIDMixin):
    __tablename__ = Relations.RECENT_SEARCHES.value
