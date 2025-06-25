# pyright: reportUninitializedInstanceVariable=false
from typing import Optional

from sqlalchemy import false, func, Column, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.mixins import CountMetadata, UpdatedAtMixin
from db.models.templates.standard import StandardBase
from db.models.types import (
    JurisdictionTypeLiteral,
    AgencyTypeLiteral,
    timestamp_tz,
    ApprovalStatusLiteral,
)
from middleware.enums import Relations


class Agency(StandardBase, CountMetadata, UpdatedAtMixin):
    __tablename__ = Relations.AGENCIES.value

    name: Mapped[str]
    homepage_url: Mapped[str | None]
    jurisdiction_type: Mapped[JurisdictionTypeLiteral]
    lat: Mapped[float | None]
    lng: Mapped[float | None]
    defunct_year: Mapped[str | None]
    agency_type: Mapped[AgencyTypeLiteral]
    multi_agency: Mapped[bool] = mapped_column(server_default=false())
    no_web_presence: Mapped[bool] = mapped_column(server_default=false())
    airtable_agency_last_modified: Mapped[timestamp_tz] = mapped_column(
        server_default=func.current_timestamp()
    )
    approval_status: Mapped[ApprovalStatusLiteral]
    rejection_reason: Mapped[str | None]
    last_approval_editor = Column(String, nullable=True)
    submitter_contact: Mapped[str | None]
    agency_created: Mapped[timestamp_tz] = mapped_column(
        server_default=func.current_timestamp()
    )
    creator_user_id: Mapped[int | None] = mapped_column(ForeignKey("public.users.id"))

    # relationships
    creator: Mapped["User"] = relationship(
        argument="User", back_populates="created_agencies", uselist=False
    )
    locations: Mapped[list["LocationExpanded"]] = relationship(
        argument="LocationExpanded",
        secondary="public.link_agencies_locations",
        primaryjoin="LinkAgencyLocation.agency_id == Agency.id",
        secondaryjoin="LinkAgencyLocation.location_id == LocationExpanded.id",
        back_populates="agencies",
    )

    data_sources: Mapped[list["DataSourceExpanded"]] = relationship(
        argument="DataSourceExpanded",
        secondary="public.link_agencies_data_sources",
        primaryjoin="LinkAgencyDataSource.agency_id == Agency.id",
        secondaryjoin="LinkAgencyDataSource.data_source_id == DataSourceExpanded.id",
        back_populates="agencies",
    )
