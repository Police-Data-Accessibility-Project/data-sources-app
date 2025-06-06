from datetime import date
from typing import Optional, get_args

from sqlalchemy import (
    Column,
    text as text_func,
    Text,
    String,
    ForeignKey,
    Enum,
    Integer,
    UniqueConstraint,
    CheckConstraint,
    DateTime,
)
from sqlalchemy.dialects.postgresql import (
    ARRAY,
    ENUM as pgEnum,
    JSONB,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.sql.expression import false, func

from database_client.enums import AccessType
from database_client.models.base import Base
from database_client.models.helpers import (
    iter_with_special_cases,
    get_iter_model_list_of_dict,
    make_get_iter_model_list_of_dict,
)
from database_client.models.mixins import (
    CountMetadata,
    CountSubqueryMetadata,
    CreatedAtMixin,
    UserIDMixin,
    LocationIDMixin,
    DataRequestIDMixin,
    DataSourceIDMixin,
    IterWithSpecialCasesMixin,
)
from database_client.models.templates.standard import StandardBase
from database_client.models.types import (
    ExternalAccountTypeLiteral,
    RecordTypeLiteral,
    RequestStatusLiteral,
    OperationTypeLiteral,
    JurisdictionTypeLiteral,
    ApprovalStatusLiteral,
    URLStatusLiteral,
    RetentionScheduleLiteral,
    DetailLevelLiteral,
    UpdateMethodLiteral,
    RequestUrgencyLiteral,
    LocationTypeLiteral,
    LocationTypePGEnum,
    EventTypeDataRequestLiteral,
    EventTypeDataSourceLiteral,
    AgencyAggregationLiteral,
    AgencyTypeLiteral,
    text,
    timestamp_tz,
    timestamp,
    str_255,
)
from middleware.enums import Relations


class Agency(StandardBase, CountMetadata):
    __tablename__ = Relations.AGENCIES.value

    name: Mapped[str]
    homepage_url: Mapped[Optional[str]]
    jurisdiction_type: Mapped[JurisdictionTypeLiteral]
    lat: Mapped[Optional[float]]
    lng: Mapped[Optional[float]]
    defunct_year: Mapped[Optional[str]]
    agency_type: Mapped[AgencyTypeLiteral]
    multi_agency: Mapped[bool] = mapped_column(server_default=false())
    no_web_presence: Mapped[bool] = mapped_column(server_default=false())
    airtable_agency_last_modified: Mapped[timestamp_tz] = mapped_column(
        server_default=func.current_timestamp()
    )
    approval_status: Mapped[ApprovalStatusLiteral]
    rejection_reason: Mapped[Optional[str]]
    last_approval_editor = Column(String, nullable=True)
    submitter_contact: Mapped[Optional[str]]
    agency_created: Mapped[timestamp_tz] = mapped_column(
        server_default=func.current_timestamp()
    )
    creator_user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("public.users.id")
    )

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


class AgencyExpanded(Agency):

    __tablename__ = Relations.AGENCIES_EXPANDED.value
    id = mapped_column(None, ForeignKey("public.agencies.id"), primary_key=True)

    submitted_name = Column(String)

    state_name = Column(String)  #
    locality_name = Column(String)  #
    state_iso: Mapped[Optional[str]]
    municipality: Mapped[Optional[str]]
    county_fips: Mapped[Optional[str]]
    county_name: Mapped[Optional[str]]

    # Some attributes need to be overwritten by the attributes provided by locations_expanded
    state_iso = Column(String)
    county_name = Column(String)


class TableCountLog(StandardBase, CreatedAtMixin):
    __tablename__ = Relations.TABLE_COUNT_LOG.value

    table_name: Mapped[str]
    count: Mapped[int]


class County(StandardBase):
    __tablename__ = Relations.COUNTIES.value
    __table_args__ = (UniqueConstraint("fips", name="unique_fips"),)

    fips: Mapped[str]
    name: Mapped[Optional[text]]
    lat: Mapped[Optional[float]]
    lng: Mapped[Optional[float]]
    population: Mapped[Optional[int]]
    agencies: Mapped[Optional[text]]
    airtable_county_last_modified: Mapped[Optional[text]]
    airtable_county_created: Mapped[Optional[text]]
    state_id: Mapped[Optional[int]] = mapped_column(ForeignKey("public.us_states.id"))

    # Relationships
    state = relationship("USState", back_populates="counties", uselist=False)
    locations = relationship("Location", back_populates="county")
    localities = relationship("Locality", back_populates="county")


class Locality(StandardBase):
    __tablename__ = Relations.LOCALITIES.value
    __table_args__ = (
        CheckConstraint("name NOT LIKE '%,%'", name="localities_name_check"),
    )

    name: Mapped[Optional[Text]] = mapped_column(Text)
    county_id: Mapped[int] = mapped_column(ForeignKey("counties.id"))

    # Relationships
    county = relationship("County", back_populates="localities", uselist=False)
    location = relationship("Location", back_populates="locality", uselist=False)


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
        secondary="public.link_agencies_locations",
        primaryjoin="LocationExpanded.id == LinkAgencyLocation.location_id",
        secondaryjoin="LinkAgencyLocation.agency_id == AgencyExpanded.id",
        back_populates="locations",
    )


class ExternalAccount(Base, UserIDMixin):
    __tablename__ = Relations.EXTERNAL_ACCOUNTS.value
    row_id: Mapped[int] = mapped_column(primary_key=True)
    account_type: Mapped[ExternalAccountTypeLiteral]
    account_identifier: Mapped[str_255]
    linked_at: Mapped[Optional[timestamp]] = mapped_column(server_default=func.now())


class USState(StandardBase):
    __tablename__ = Relations.US_STATES.value

    state_iso: Mapped[str] = mapped_column(String(255), nullable=False)
    state_name: Mapped[str] = mapped_column(String(255))

    # Relationships
    locations = relationship("Location", back_populates="state")
    counties = relationship("County", back_populates="state")


class DataRequest(
    StandardBase, CountMetadata, CountSubqueryMetadata, IterWithSpecialCasesMixin
):
    __tablename__ = Relations.DATA_REQUESTS.value

    special_cases = {
        "data_sources": make_get_iter_model_list_of_dict("data_sources"),
        "locations": make_get_iter_model_list_of_dict("locations"),
    }

    submission_notes: Mapped[Optional[text]]
    request_status: Mapped[RequestStatusLiteral] = mapped_column(
        server_default="Intake"
    )
    archive_reason: Mapped[Optional[text]]
    date_created: Mapped[timestamp_tz]
    date_status_last_changed: Mapped[Optional[timestamp_tz]]
    creator_user_id: Mapped[Optional[int]]
    internal_notes: Mapped[Optional[text]]
    record_types_required: Mapped[Optional[ARRAY[RecordTypeLiteral]]] = mapped_column(
        ARRAY(Enum(*get_args(RecordTypeLiteral), name="record_type"), as_tuple=True)
    )
    pdap_response: Mapped[Optional[text]]
    coverage_range: Mapped[Optional[str]]
    data_requirements: Mapped[Optional[text]]
    request_urgency: Mapped[RequestUrgencyLiteral] = mapped_column(
        server_default="Indefinite/Unknown"
    )
    title: Mapped[text]

    # TODO: Is there a way to generalize the below logic?
    locations: Mapped[list["LocationExpanded"]] = relationship(
        argument="LocationExpanded",
        secondary="public.link_locations_data_requests",
        primaryjoin="DataRequest.id == LinkLocationDataRequest.data_request_id",
        secondaryjoin="LocationExpanded.id == LinkLocationDataRequest.location_id",
    )
    github_issue_info = relationship(
        argument="DataRequestsGithubIssueInfo",
        back_populates="data_request",
        uselist=False,
    )


class DataRequestExpanded(DataRequest):
    id = mapped_column(None, ForeignKey("public.data_requests.id"), primary_key=True)

    __tablename__ = Relations.DATA_REQUESTS_EXPANDED.value
    github_issue_url: Mapped[Optional[text]]
    github_issue_number: Mapped[Optional[int]]

    data_sources: Mapped[list["DataSourceExpanded"]] = relationship(
        argument="DataSourceExpanded",
        secondary="public.link_data_sources_data_requests",
        primaryjoin="DataRequestExpanded.id == LinkDataSourceDataRequest.request_id",
        secondaryjoin="DataSourceExpanded.id == LinkDataSourceDataRequest.data_source_id",
        back_populates="data_requests",
    )


class DataSource(
    StandardBase,
    CountMetadata,
    CountSubqueryMetadata,
    CreatedAtMixin,
    IterWithSpecialCasesMixin,
):
    __tablename__ = Relations.DATA_SOURCES.value

    special_cases = {
        "agencies": make_get_iter_model_list_of_dict("agencies"),
        "data_requests": make_get_iter_model_list_of_dict("data_requests"),
    }

    name: Mapped[str]
    description: Mapped[Optional[str]]
    source_url: Mapped[Optional[str]]
    agency_supplied: Mapped[Optional[bool]]
    supplying_entity: Mapped[Optional[str]]
    agency_originated: Mapped[Optional[bool]]
    agency_aggregation: Mapped[Optional[AgencyAggregationLiteral]]
    coverage_start: Mapped[Optional[date]]
    coverage_end: Mapped[Optional[date]]
    updated_at: Mapped[Optional[date]] = Column(DateTime, default=func.now())
    detail_level: Mapped[Optional[DetailLevelLiteral]]
    # Note: Below is an array of enums in Postgres but this is cumbersome to convey in SQLAlchemy terms
    access_types = Column(
        ARRAY(pgEnum(*[e.value for e in AccessType], name="access_type"))
    )
    data_portal_type: Mapped[Optional[str]]
    record_formats = Column(ARRAY(String))
    update_method: Mapped[Optional[UpdateMethodLiteral]]
    tags = Column(ARRAY(String))
    readme_url: Mapped[Optional[str]]
    originating_entity: Mapped[Optional[str]]
    retention_schedule: Mapped[Optional[RetentionScheduleLiteral]]
    scraper_url: Mapped[Optional[str]]
    submission_notes: Mapped[Optional[str]]
    rejection_note: Mapped[Optional[str]]
    last_approval_editor: Mapped[Optional[int]]
    submitter_contact_info: Mapped[Optional[str]]
    agency_described_not_in_database: Mapped[Optional[str]]
    data_portal_type_other: Mapped[Optional[str]]
    data_source_request: Mapped[Optional[str]]
    broken_source_url_as_of: Mapped[Optional[date]]
    access_notes: Mapped[Optional[text]]
    url_status: Mapped[URLStatusLiteral] = Column(
        Enum(*get_args(URLStatusLiteral), name="url_status"), server_default="ok"
    )
    approval_status: Mapped[ApprovalStatusLiteral]
    record_type_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("public.record_types.id")
    )
    approval_status_updated_at: Mapped[Optional[timestamp_tz]]

    # Relationships
    locations: Mapped[list[Location]] = relationship(
        argument="Location",
        secondary="public.link_locations_data_sources_view",
        primaryjoin="LinkLocationDataSourceView.data_source_id == DataSource.id",
        secondaryjoin="LinkLocationDataSourceView.location_id == Location.id",
        back_populates="data_sources",
        viewonly=True,
    )


class DataSourceExpanded(DataSource):
    id = mapped_column(None, ForeignKey("public.data_sources.id"), primary_key=True)

    __tablename__ = Relations.DATA_SOURCES_EXPANDED.value

    record_type_name: Mapped[Optional[str]]

    agencies: Mapped[list[Agency]] = relationship(
        argument="Agency",
        secondary="public.link_agencies_data_sources",
        primaryjoin="LinkAgencyDataSource.data_source_id == DataSourceExpanded.id",
        secondaryjoin="LinkAgencyDataSource.agency_id == Agency.id",
        back_populates="data_sources",
    )

    data_requests: Mapped[list[DataRequestExpanded]] = relationship(
        argument="DataRequestExpanded",
        secondary="public.link_data_sources_data_requests",
        primaryjoin="LinkDataSourceDataRequest.data_source_id == DataSourceExpanded.id",
        secondaryjoin="LinkDataSourceDataRequest.request_id == DataRequestExpanded.id",
        back_populates="data_sources",
    )


class DataSourceArchiveInfo(Base):
    __tablename__ = Relations.DATA_SOURCES_ARCHIVE_INFO.value

    data_source_id: Mapped[str] = mapped_column(
        ForeignKey("public.data_sources.id"), primary_key=True
    )
    update_frequency: Mapped[Optional[str]]
    last_cached: Mapped[Optional[timestamp]]
    next_cached: Mapped[Optional[timestamp]]


class DataRequestsGithubIssueInfo(StandardBase, DataRequestIDMixin):
    __tablename__ = Relations.DATA_REQUESTS_GITHUB_ISSUE_INFO.value

    github_issue_url: Mapped[str]
    github_issue_number: Mapped[int]


class RecordCategory(StandardBase):
    __tablename__ = Relations.RECORD_CATEGORIES.value

    # TODO: Update so that names reference literals
    name: Mapped[str_255]
    description: Mapped[Optional[text]]

    # Relationships
    record_types: Mapped[list["RecordType"]] = relationship(
        argument="RecordType",
        back_populates="record_categories",
    )


class RecordType(StandardBase):
    __tablename__ = Relations.RECORD_TYPES.value

    name: Mapped[str_255]
    category_id: Mapped[int] = mapped_column(ForeignKey("public.record_categories.id"))
    description: Mapped[Optional[text]]

    # Relationships
    record_categories: Mapped[list[RecordCategory]] = relationship(
        argument="RecordCategory",
        back_populates="record_types",
    )


class ResetToken(StandardBase, UserIDMixin):
    __tablename__ = Relations.RESET_TOKENS.value

    token: Mapped[Optional[text]]
    create_date: Mapped[timestamp] = mapped_column(
        server_default=func.current_timestamp()
    )


class TestTable(StandardBase):
    __tablename__ = Relations.TEST_TABLE.value

    pet_name: Mapped[Optional[str_255]]
    species: Mapped[Optional[str_255]]


class User(StandardBase, CreatedAtMixin):
    __tablename__ = Relations.USERS.value

    updated_at: Mapped[Optional[timestamp_tz]]
    email: Mapped[text] = mapped_column(unique=True)
    password_digest: Mapped[Optional[text]]
    api_key: Mapped[Optional[str]] = mapped_column(
        server_default=text_func("generate_api_key()")
    )
    role: Mapped[Optional[text]]

    # Relationships
    created_agencies = relationship(
        argument="Agency",
        back_populates="creator",
    )
    permissions = relationship(
        argument="Permission",
        secondary="public.user_permissions",
        primaryjoin="User.id == UserPermission.user_id",
        secondaryjoin="UserPermission.permission_id == Permission.id",
    )
    data_request_events = relationship(
        argument="DataRequestPendingEventNotification",
        secondary="public.data_request_user_notification_queue",
        primaryjoin="User.id == DataRequestUserNotificationQueue.user_id",
        secondaryjoin="DataRequestUserNotificationQueue.event_id == DataRequestPendingEventNotification.id",
    )
    data_source_events = relationship(
        argument="DataSourcePendingEventNotification",
        secondary="public.data_source_user_notification_queue",
        primaryjoin="User.id == DataSourceUserNotificationQueue.user_id",
        secondaryjoin="DataSourceUserNotificationQueue.event_id == DataSourcePendingEventNotification.id",
    )


class Permission(StandardBase):
    __tablename__ = Relations.PERMISSIONS.value

    permission_name: Mapped[str_255]
    description: Mapped[Optional[text]]


class UserPermission(StandardBase, UserIDMixin):
    __tablename__ = Relations.USER_PERMISSIONS.value

    permission_id: Mapped[int] = mapped_column(ForeignKey("public.permissions.id"))


class PendingUser(StandardBase, CreatedAtMixin):
    __tablename__ = Relations.PENDING_USERS.value

    email: Mapped[text] = mapped_column(unique=True)
    password_digest: Mapped[Optional[text]]
    validation_token: Mapped[Optional[text]]


class DependentLocation(Base):
    __tablename__ = Relations.DEPENDENT_LOCATIONS.value
    __mapper_args__ = {"primary_key": ["parent_location_id", "dependent_location_id"]}

    parent_location_id: Mapped[int] = mapped_column(ForeignKey("public.locations.id"))
    dependent_location_id: Mapped[int] = mapped_column(
        ForeignKey("public.locations.id")
    )


class DataRequestPendingEventNotification(
    StandardBase, CreatedAtMixin, DataRequestIDMixin
):
    __tablename__ = Relations.DATA_REQUESTS_PENDING_EVENT_NOTIFICATIONS.value
    event_type: Mapped[EventTypeDataRequestLiteral] = mapped_column(
        Enum(*get_args(EventTypeDataRequestLiteral), name="event_type_data_request")
    )


class DataSourcePendingEventNotification(
    StandardBase, CreatedAtMixin, DataSourceIDMixin
):
    __tablename__ = Relations.DATA_SOURCES_PENDING_EVENT_NOTIFICATIONS.value

    event_type: Mapped[EventTypeDataSourceLiteral] = mapped_column(
        Enum(*get_args(EventTypeDataSourceLiteral), name="event_type_data_source")
    )


class DataRequestUserNotificationQueue(StandardBase, UserIDMixin):
    __tablename__ = Relations.DATA_REQUESTS_USER_NOTIFICATION_QUEUE.value

    event_id: Mapped[int] = mapped_column(
        ForeignKey("public.data_request_pending_event_notification.id")
    )
    sent_at: Mapped[Optional[timestamp]]

    # Relationships
    pending_event_notification = relationship(
        argument="DataRequestPendingEventNotification",
        primaryjoin="DataRequestUserNotificationQueue.event_id == DataRequestPendingEventNotification.id",
        uselist=False,
    )


class DataSourceUserNotificationQueue(StandardBase, UserIDMixin):
    __tablename__ = Relations.DATA_SOURCES_USER_NOTIFICATION_QUEUE.value

    event_id: Mapped[int] = mapped_column(
        ForeignKey("public.data_source_pending_event_notification.id")
    )
    sent_at: Mapped[Optional[timestamp]]

    # Relationships
    pending_event_notification = relationship(
        argument="DataSourcePendingEventNotification",
        primaryjoin="DataSourceUserNotificationQueue.event_id == DataSourcePendingEventNotification.id",
        uselist=False,
    )


class RecentSearch(StandardBase, CreatedAtMixin, UserIDMixin, LocationIDMixin):
    __tablename__ = Relations.RECENT_SEARCHES.value


class RecentSearchExpanded(StandardBase, CountMetadata, UserIDMixin, LocationIDMixin):
    __tablename__ = Relations.RECENT_SEARCHES_EXPANDED.value

    state_name: Mapped[str]
    county_name: Mapped[str]
    locality_name: Mapped[str]
    location_type: Mapped[LocationTypeLiteral]
    record_categories = mapped_column(ARRAY(String, as_tuple=True))


class ChangeLog(StandardBase, CreatedAtMixin):
    __tablename__ = Relations.CHANGE_LOG.value

    operation_type: Mapped[OperationTypeLiteral]
    table_name: Mapped[str]
    affected_id: Mapped[int]
    old_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    new_data: Mapped[dict] = mapped_column(JSONB, nullable=True)


class NotificationLog(StandardBase, CreatedAtMixin):
    __tablename__ = Relations.NOTIFICATION_LOG.value

    user_count: Mapped[int]


class DistinctSourceURL(Base):
    __tablename__ = Relations.DISTINCT_SOURCE_URLS.value

    base_url: Mapped[str] = mapped_column(primary_key=True)
    original_url: Mapped[str]
    rejection_note: Mapped[str]
    approval_status: Mapped[str]
