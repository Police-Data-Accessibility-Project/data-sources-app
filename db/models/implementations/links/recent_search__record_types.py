from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from db.models.mixins import RecordTypeIDMixin
from db.models.templates.standard import StandardBase
from middleware.enums import Relations


class LinkRecentSearchRecordTypes(StandardBase, RecordTypeIDMixin):
    __tablename__ = Relations.LINK_RECENT_SEARCH_RECORD_TYPES.value

    recent_search_id: Mapped[int] = mapped_column(
        ForeignKey("public.recent_searches.id")
    )
