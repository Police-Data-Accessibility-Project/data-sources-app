# pyright: reportUninitializedInstanceVariable=false
from typing import Optional

from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.templates.standard import StandardBase
from db.models.types import text
from middleware.enums import Relations


class County(StandardBase):
    __tablename__ = Relations.COUNTIES.value
    __table_args__ = (UniqueConstraint("fips", name="unique_fips"),)

    fips: Mapped[str]
    name: Mapped[text | None]
    lat: Mapped[float | None]
    lng: Mapped[float | None]
    population: Mapped[int | None]
    agencies: Mapped[text | None]
    airtable_county_last_modified: Mapped[text | None]
    airtable_county_created: Mapped[text | None]
    state_id: Mapped[int | None] = mapped_column(ForeignKey("public.us_states.id"))

    # Relationships
    state = relationship("USState", back_populates="counties", uselist=False)
    locations = relationship("Location", back_populates="county")
    localities = relationship("Locality", back_populates="county")
