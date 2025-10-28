# pyright: reportUninitializedInstanceVariable=false

from sqlalchemy import false, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.helpers import enum_column
from db.models.mixins import CountMetadata, UpdatedAtMixin
from db.models.templates.standard import StandardBase
from db.models.types import (
    JurisdictionTypeLiteral,
    AgencyTypeLiteral,
    timestamp_tz,
)
from middleware.enums import Relations, JurisdictionType, AgencyType


class Agency(StandardBase, CountMetadata, UpdatedAtMixin):
    __tablename__ = Relations.AGENCIES.value

    name: Mapped[str]
    jurisdiction_type: Mapped[JurisdictionType] = enum_column(
        name="jurisdiction_type",
        enum=JurisdictionType,
    )
    defunct_year: Mapped[str | None]
    agency_type: Mapped[AgencyType] = enum_column(
        name="agency_type",
        enum=AgencyType,
    )
    no_web_presence: Mapped[bool] = mapped_column(server_default=false())
    created_at: Mapped[timestamp_tz] = mapped_column(
        server_default=func.current_timestamp()
    )

    # relationships
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
    meta_urls: Mapped[list["AgencyMetaURL"]] = relationship(
        argument="AgencyMetaURL",
        primaryjoin="AgencyMetaURL.agency_id == Agency.id",
    )
