# pyright: reportUninitializedInstanceVariable=false
from typing import Optional

from sqlalchemy import ForeignKey, Column, String
from sqlalchemy.orm import mapped_column, Mapped

from db.models.implementations.core.agency.core import Agency
from middleware.enums import Relations


class AgencyExpanded(Agency):

    __tablename__ = Relations.AGENCIES_EXPANDED.value
    id = mapped_column(None, ForeignKey("public.agencies.id"), primary_key=True)

    submitted_name = Column(String)

    state_name = Column(String)  #
    locality_name = Column(String)  #
    state_iso: Mapped[str | None]
    municipality: Mapped[str | None]
    county_fips: Mapped[str | None]
    county_name: Mapped[str | None]

    # Some attributes need to be overwritten by the attributes provided by locations_expanded
    state_iso = Column(String)
    county_name = Column(String)
