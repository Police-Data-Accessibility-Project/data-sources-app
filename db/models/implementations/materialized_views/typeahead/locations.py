from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base
from db.models.mixins import ViewMixin


class TypeaheadLocations(
    Base,
    ViewMixin
):

    __tablename__ = "typeahead_locations"
    __table_args__ = (
        PrimaryKeyConstraint("location_id"),
        {"info": "view"}
    )

    location_id: Mapped[int] = mapped_column()
    search_name: Mapped[str] = mapped_column()
    display_name: Mapped[str] = mapped_column()
    type: Mapped[str] = mapped_column()
    state_name: Mapped[str] = mapped_column()
    county_name: Mapped[str] = mapped_column()
    locality_name: Mapped[str] = mapped_column()