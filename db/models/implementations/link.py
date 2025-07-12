from sqlalchemy import ForeignKey, Column, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.base import Base
from db.models.mixins import (
    DataSourceIDMixin,
    CountMetadata,
    CreatedAtMixin,
    UserIDMixin,
    LocationIDMixin,
    DataRequestIDMixin,
    RecordTypeIDMixin,
)
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


class LinkAgencyLocation(StandardBase):
    __tablename__ = Relations.LINK_AGENCIES_LOCATIONS.value

    location_id: Mapped[int] = mapped_column(
        ForeignKey("public.locations.id"), primary_key=True
    )
    agency_id: Mapped[int] = mapped_column(
        ForeignKey("public.agencies.id"), primary_key=True
    )


class LinkDataSourceDataRequest(StandardBase, DataSourceIDMixin):
    __tablename__ = Relations.LINK_DATA_SOURCES_DATA_REQUESTS.value

    request_id: Mapped[int] = mapped_column(ForeignKey("public.data_requests.id"))


class LinkUserFollowedLocation(
    StandardBase, CountMetadata, CreatedAtMixin, UserIDMixin, LocationIDMixin
):
    __tablename__ = Relations.LINK_USER_FOLLOWED_LOCATION.value

    record_types = relationship(
        "RecordType",
        secondary="public.link_follow_record_types",
        primaryjoin="LinkUserFollowedLocation.id == LinkFollowRecordType.follow_id",
        secondaryjoin="LinkFollowRecordType.record_type_id == RecordType.id",
    )


class LinkFollowRecordType(StandardBase, RecordTypeIDMixin):
    __tablename__ = Relations.LINK_FOLLOW_RECORD_TYPES.value

    follow_id: Mapped[int] = mapped_column(
        ForeignKey("public.link_user_followed_location.id")
    )


class LinkLocationDataRequest(StandardBase, LocationIDMixin, DataRequestIDMixin):
    __tablename__ = Relations.LINK_LOCATIONS_DATA_REQUESTS.value


class LinkRecentSearchRecordCategories(StandardBase):
    __tablename__ = Relations.LINK_RECENT_SEARCH_RECORD_CATEGORIES.value

    recent_search_id: Mapped[int] = mapped_column(
        ForeignKey("public.recent_searches.id")
    )
    record_category_id: Mapped[int] = mapped_column(
        ForeignKey("public.record_categories.id")
    )


class LinkRecentSearchRecordTypes(StandardBase, RecordTypeIDMixin):
    __tablename__ = Relations.LINK_RECENT_SEARCH_RECORD_TYPES.value

    recent_search_id: Mapped[int] = mapped_column(
        ForeignKey("public.recent_searches.id")
    )


class LinkLocationDataSourceView(Base):
    __tablename__ = Relations.LINK_LOCATIONS_DATA_SOURCES_VIEW.value
    location_id = Column(Integer, primary_key=True)
    data_source_id = Column(Integer, primary_key=True)
