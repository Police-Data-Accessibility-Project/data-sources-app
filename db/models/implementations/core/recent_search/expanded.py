from sqlalchemy import String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from db.models.mixins import CountMetadata, UserIDMixin, LocationIDMixin
from db.models.templates.standard import StandardBase
from db.models.types import LocationTypeLiteral
from middleware.enums import Relations


class RecentSearchExpanded(StandardBase, CountMetadata, UserIDMixin, LocationIDMixin):
    __tablename__ = Relations.RECENT_SEARCHES_EXPANDED.value

    state_name: Mapped[str]
    county_name: Mapped[str]
    locality_name: Mapped[str]
    location_type: Mapped[LocationTypeLiteral]
    record_categories = mapped_column(ARRAY(String, as_tuple=True))
