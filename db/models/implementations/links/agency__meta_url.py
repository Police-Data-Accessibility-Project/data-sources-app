from sqlalchemy import Column, Integer, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped

from db.models.base import Base
from db.models.implementations.core.agency.meta_urls.sqlalchemy import MetaURL
from db.models.mixins import CreatedAtMixin, AgencyIDMixin


class LinkAgencyMetaURL(
    Base,
    CreatedAtMixin,
    AgencyIDMixin,
):
    __tablename__ = "link_agencies__meta_urls"
    __table_args__ = (
        PrimaryKeyConstraint(
            "agency_id",
            "meta_url_id",
        ),
    )

    meta_url_id: Mapped[int] = Column(
        Integer,
        ForeignKey(MetaURL.__table__.c.id),
        nullable=False,
    )
