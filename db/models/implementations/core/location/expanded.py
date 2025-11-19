from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import Mapped, relationship

from db.models.mixins import CountMetadata, IterWithSpecialCasesMixin
from db.models.templates.standard import StandardBase
from db.models.types import LocationTypePGEnum
from middleware.enums import Relations


class LocationExpanded(StandardBase, CountMetadata, IterWithSpecialCasesMixin):
    __tablename__ = Relations.LOCATIONS_EXPANDED.value
    __table_args__ = {"extend_existing": True}

    type = Column(LocationTypePGEnum, nullable=False)
    state_name = Column(String)
    state_iso = Column(String)
    county_name = Column(String)
    county_fips = Column(String)
    locality_name = Column(String)
    state_id = Column(Integer)
    county_id = Column(Integer)
    locality_id = Column(Integer)
    display_name = Column(String)
    full_display_name = Column(String)

    # relationships

    agencies: Mapped[list["AgencyExpanded"]] = relationship(
        argument="AgencyExpanded",
        secondary="public.link_agencies__locations",
        primaryjoin="LocationExpanded.id == LinkAgencyLocation.location_id",
        secondaryjoin="LinkAgencyLocation.agency_id == AgencyExpanded.id",
        back_populates="locations",
    )
