from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from db.models.templates.standard import StandardBase
from middleware.enums import Relations


class LinkAgencyDataSource(StandardBase):
    __tablename__ = Relations.LINK_AGENCIES_DATA_SOURCES.value

    data_source_id: Mapped[int] = mapped_column(
        ForeignKey("public.data_sources.id"), primary_key=True
    )
    agency_id: Mapped[int] = mapped_column(
        ForeignKey("public.agencies.id"), primary_key=True
    )
