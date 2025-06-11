from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.mixins import IterWithSpecialCasesMixin
from db.models.templates.standard import StandardBase
from db.models.types import LocationTypePGEnum
from middleware.enums import Relations


class Location(StandardBase, IterWithSpecialCasesMixin):
    __tablename__ = Relations.LOCATIONS.value

    type = Column(LocationTypePGEnum, nullable=False)
    state_id: Mapped[int] = mapped_column(
        ForeignKey("public.us_states.id"), nullable=False
    )
    county_id: Mapped[int] = mapped_column(ForeignKey("counties.id"))
    locality_id: Mapped[int] = mapped_column(ForeignKey("localities.id"))
    lat: Mapped[float]
    lng: Mapped[float]

    # Relationships
    county = relationship(argument="County", back_populates="locations", uselist=False)
    locality = relationship(
        argument="Locality", back_populates="location", uselist=False
    )
    state = relationship(argument="USState", back_populates="locations", uselist=False)

    data_sources = relationship(
        "DataSource",
        secondary="public.link_locations_data_sources_view",
        primaryjoin="Location.id == LinkLocationDataSourceView.location_id",
        secondaryjoin="LinkLocationDataSourceView.data_source_id == DataSource.id",
        back_populates="locations",
        viewonly=True,
    )
