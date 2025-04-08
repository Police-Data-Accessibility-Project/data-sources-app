from datetime import datetime, date
from typing import Optional, Literal, get_args, Callable

from sqlalchemy.dialects import postgresql
from typing_extensions import Annotated


from sqlalchemy import (
    Column,
    text as text_func,
    Text,
    String,
    ForeignKey,
    Enum,
    Integer,
    UniqueConstraint,
    inspect,
    CheckConstraint,
    DateTime,
    PrimaryKeyConstraint,
    Identity,
)
from sqlalchemy.dialects.postgresql import (
    ARRAY,
    DATE,
    DATERANGE,
    TIMESTAMP,
    ENUM as pgEnum,
    JSONB,
)
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    column_property,
    MappedColumn,
)
from sqlalchemy.sql.expression import false, func

from database_client.enums import LocationType, AccessType
from middleware.enums import Relations, PermissionsEnum

ExternalAccountTypeLiteral = Literal["github"]
RecordTypeLiteral = Literal[
    "Dispatch Recordings",
    "Arrest Records",
    "Citations",
    "Incarceration Records",
    "Booking Reports",
    "Budgets & Finances",
    "Misc Police Activity",
    "Geographic",
    "Crime Maps & Reports",
    "Other",
    "Annual & Monthly Reports",
    "Resources",
    "Dispatch Logs",
    "Sex Offender Registry",
    "Officer Involved Shootings",
    "Daily Activity Logs",
    "Crime Statistics",
    "Records Request Info",
    "Policies & Contracts",
    "Stops",
    "Media Bulletins",
    "Training & Hiring Info",
    "Personnel Records",
    "Contact Info & Agency Meta",
    "Incident Reports",
    "Calls for Service",
    "Accident Reports",
    "Use of Force Reports",
    "Complaints & Misconduct",
    "Vehicle Pursuits",
    "Court Cases",
    "Surveys",
    "Field Contacts",
    "Wanted Persons",
    "List of Data Sources",
    "Car GPS",
]
RequestStatusLiteral = Literal[
    "Intake",
    "Active",
    "Complete",
    "Request withdrawn",
    "Waiting for scraper",
    "Archived",
    "Ready to start",
    "Waiting for FOIA",
    "Waiting for requestor",
]

OperationTypeLiteral = Literal["UPDATE", "DELETE", "INSERT"]

JurisdictionTypeLiteral = Literal[
    "federal", "state", "county", "local", "port", "tribal", "transit", "school"
]
ApprovalStatusLiteral = Literal[
    "rejected", "approved", "needs identification", "pending"
]
URLStatusLiteral = Literal["available", "none found", "ok", "broken"]
RetentionScheduleLiteral = Literal[
    "1-10 years",
    "< 1 week",
    "1 day",
    "Future only",
    "< 1 day",
    "< 1 year",
    "1 month",
    "1 week",
    "> 10 years",
]
DetailLevelLiteral = Literal[
    "Individual record", "Aggregated records", "Summarized totals"
]
AccessTypeLiteral = Literal["Web page", "API", "Download"]
UpdateMethodLiteral = Literal["Insert", "No updates", "Overwrite"]
RequestUrgencyLiteral = Literal[
    "urgent",
    "somewhat_urgent",
    "not_urgent",
    "long_term",
    "indefinite_unknown",
]
LocationTypeLiteral = Literal["State", "County", "Locality"]

LocationTypePGEnum = postgresql.ENUM(
    LocationType.STATE.value,
    LocationType.COUNTY.value,
    LocationType.LOCALITY.value,
    name="location_type",
)


EventTypeDataRequestLiteral = Literal["Request Ready to Start", "Request Complete"]
EventTypeDataSourceLiteral = Literal["Data Source Approved"]
EntityTypeLiteral = Literal["Data Request", "Data Source"]
AgencyAggregationLiteral = Literal["county", "local", "state", "federal"]
AgencyTypeLiteral = Literal[
    "incarceration",
    "law enforcement",
    "aggregated",
    "court",
    "unknown",
]

text = Annotated[Text, None]
timestamp_tz = Annotated[
    TIMESTAMP, mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
]
timestamp = Annotated[TIMESTAMP, None]
daterange = Annotated[DATERANGE, None]
str_255 = Annotated[String, 255]


class Base(DeclarativeBase):
    __table_args__ = {"schema": "public"}
    type_annotation_map = {
        text: Text,
        date: DATE,
        timestamp: TIMESTAMP,
        daterange: DATERANGE,
        str_255: String(255),
    }

    @hybrid_method
    def to_dict(cls, subquery_parameters=[]) -> dict:
        # Calls the class's __iter__ implementation
        dict_result = dict(cls)
        keyorder = cls.__mapper__.column_attrs.items()

        for param in subquery_parameters:
            if param.linking_column not in dict_result:
                dict_result[param.linking_column] = []

        sorted_dict = {
            col: dict_result[col] for col, descriptor in keyorder if col in dict_result
        }
        sorted_dict.update(dict_result)

        return sorted_dict


class CountMetadata:
    @hybrid_method
    def count(
        cls,
        data: list[dict],
        **kwargs,
    ) -> int:
        return {"count": len(data)}


class CountSubqueryMetadata:
    @hybrid_method
    def count_subquery(
        cls, data: list[dict], subquery_parameters, **kwargs
    ) -> Optional[dict[str, int]]:
        if not subquery_parameters or len(data) != 1:
            return None

        subquery_counts = {}
        for subquery_param in subquery_parameters:
            linking_column = subquery_param.linking_column
            key = linking_column + "_count"
            count = len(data[0][linking_column])
            subquery_counts.update({key: count})

        return subquery_counts


class LinkAgencyDataSource(Base):
    __tablename__ = Relations.LINK_AGENCIES_DATA_SOURCES.value

    id: Mapped[int] = Column(Integer, primary_key=False, server_default=Identity())
    data_source_id: Mapped[str] = mapped_column(
        ForeignKey("public.data_sources.id"), primary_key=True
    )
    agency_id: Mapped[str] = mapped_column(
        ForeignKey("public.agencies.id"), primary_key=True
    )


class Agency(Base, CountMetadata):
    __tablename__ = Relations.AGENCIES.value

    def __iter__(self):

        special_cases = {
            "data_sources": lambda instance: get_iter_model_list_of_dict(
                instance, attr_name="data_sources"
            ),
        }

        yield from iter_with_special_cases(self, special_cases=special_cases)

    id: Mapped[int] = mapped_column(primary_key=True)
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


class LinkAgencyLocation(Base):
    __tablename__ = Relations.LINK_AGENCIES_LOCATIONS.value

    id: Mapped[int] = mapped_column(primary_key=True)
    location_id: Mapped[int] = mapped_column(
        ForeignKey("public.locations.id"), primary_key=True
    )
    agency_id: Mapped[int] = mapped_column(
        ForeignKey("public.agencies.id"), primary_key=True
    )


class TableCountLog(Base):
    __tablename__ = Relations.TABLE_COUNT_LOG.value

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    table_name: Mapped[str]
    count: Mapped[int]
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class County(Base):
    __tablename__ = Relations.COUNTIES.value
    __table_args__ = (UniqueConstraint("fips", name="unique_fips"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    fips: Mapped[str]
    name: Mapped[Optional[text]]
    state_iso: Mapped[Optional[text]]
    lat: Mapped[Optional[float]]
    lng: Mapped[Optional[float]]
    population: Mapped[Optional[int]]
    agencies: Mapped[Optional[text]]
    airtable_county_last_modified: Mapped[Optional[text]]
    airtable_county_created: Mapped[Optional[text]]
    state_id: Mapped[Optional[int]] = mapped_column(ForeignKey("public.us_states.id"))


class Locality(Base):
    __tablename__ = Relations.LOCALITIES.value
    __table_args__ = (
        CheckConstraint("name NOT LIKE '%,%'", name="localities_name_check"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[Optional[Text]] = mapped_column(Text)
    county_id: Mapped[int] = mapped_column(ForeignKey("public.counties.id"))


class Location(Base):
    __tablename__ = Relations.LOCATIONS.value

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    type = Column(LocationTypePGEnum, nullable=False)
    state_id: Mapped[int] = mapped_column(
        ForeignKey("public.us_states.id"), nullable=False
    )
    county_id: Mapped[int] = mapped_column(ForeignKey("public.counties.id"))
    locality_id: Mapped[int] = mapped_column(ForeignKey("public.localities.id"))

    def __iter__(self):
        yield from iter_with_special_cases(self)

    # Relationships


class LocationExpanded(Base, CountMetadata):
    __tablename__ = Relations.LOCATIONS_EXPANDED.value
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
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

    def __iter__(self):
        yield from iter_with_special_cases(self)

    # relationships

    agencies: Mapped[list["AgencyExpanded"]] = relationship(
        argument="AgencyExpanded",
        secondary="public.link_agencies_locations",
        primaryjoin="LocationExpanded.id == LinkAgencyLocation.location_id",
        secondaryjoin="LinkAgencyLocation.agency_id == AgencyExpanded.id",
        back_populates="locations",
    )


class ExternalAccount(Base):
    __tablename__ = Relations.EXTERNAL_ACCOUNTS.value
    row_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("public.users.id"))
    account_type: Mapped[ExternalAccountTypeLiteral]
    account_identifier: Mapped[str_255]
    linked_at: Mapped[Optional[timestamp]] = mapped_column(server_default=func.now())


class USState(Base):
    __tablename__ = Relations.US_STATES.value

    id: Mapped[int] = mapped_column(primary_key=True)
    state_iso: Mapped[str] = mapped_column(String(255), nullable=False)
    state_name: Mapped[str] = mapped_column(String(255))


class DataRequest(Base, CountMetadata, CountSubqueryMetadata):
    __tablename__ = Relations.DATA_REQUESTS.value

    def __iter__(self):

        special_cases = {
            "data_sources": lambda instance: get_iter_model_list_of_dict(
                instance, attr_name="data_sources"
            ),
            "locations": lambda instance: get_iter_model_list_of_dict(
                instance, attr_name="locations"
            ),
        }

        yield from iter_with_special_cases(self, special_cases=special_cases)

    id: Mapped[int] = mapped_column(primary_key=True)
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


def iter_with_special_cases(instance, special_cases=None):
    """Generates key-value pairs for an instance, applying special case handling."""
    if special_cases is None:
        special_cases = {}
    for key in instance.__dict__.copy():
        # Skip the _sa_instance_state key
        if key == "_sa_instance_state":
            continue

        # Handle keys with special cases defined in the special_cases dictionary
        if key in special_cases:
            mapped_key_value_pairs = special_cases[key](instance).copy()
            for mapped_key, mapped_value in mapped_key_value_pairs:
                if mapped_value is not None:
                    yield mapped_key, mapped_value
        else:
            # General case for other keys
            value = getattr(instance, key)
            if isinstance(value, datetime) or isinstance(value, date):
                value = str(value)  # Convert datetime to string if needed
            yield key, value


def get_iter_model_list_of_dict(instance, attr_name: str):
    return [
        (
            attr_name,
            (
                [item.to_dict() for item in getattr(instance, attr_name)]
                if getattr(instance, attr_name) is not None
                else None
            ),
        )
    ]


class DataSource(Base, CountMetadata, CountSubqueryMetadata):
    __tablename__ = Relations.DATA_SOURCES.value

    def __iter__(self):

        special_cases = {
            "agencies": lambda instance: get_iter_model_list_of_dict(
                instance, attr_name="agencies"
            ),
            "data_requests": lambda instance: get_iter_model_list_of_dict(
                instance, attr_name="data_requests"
            ),
        }
        yield from iter_with_special_cases(self, special_cases)

    id: Mapped[int] = mapped_column(primary_key=True)
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
    created_at: Mapped[Optional[timestamp_tz]] = mapped_column(
        server_default=func.now()
    )
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


class LinkDataSourceDataRequest(Base):
    __tablename__ = Relations.LINK_DATA_SOURCES_DATA_REQUESTS.value

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    data_source_id: Mapped[text] = mapped_column(ForeignKey("public.data_sources.id"))
    request_id: Mapped[int] = mapped_column(ForeignKey("public.data_requests.id"))


class DataRequestsGithubIssueInfo(Base):
    __tablename__ = Relations.DATA_REQUESTS_GITHUB_ISSUE_INFO.value

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    data_request_id: Mapped[int] = mapped_column(ForeignKey("public.data_requests.id"))
    github_issue_url: Mapped[str]
    github_issue_number: Mapped[int]

    # Relationships
    data_request = relationship(
        argument="DataRequest", back_populates="github_issue_info", uselist=False
    )


class LinkUserFollowedLocation(Base, CountMetadata):
    __tablename__ = Relations.LINK_USER_FOLLOWED_LOCATION.value

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("public.users.id"))
    location_id: Mapped[int] = mapped_column(ForeignKey("public.locations.id"))


class RecordCategory(Base):
    __tablename__ = Relations.RECORD_CATEGORIES.value

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # TODO: Update so that names reference literals
    name: Mapped[str_255]
    description: Mapped[Optional[text]]

    # Relationships
    record_types: Mapped[list["RecordType"]] = relationship(
        argument="RecordType",
        back_populates="record_categories",
    )


class RecordType(Base):
    __tablename__ = Relations.RECORD_TYPES.value

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str_255]
    category_id: Mapped[int] = mapped_column(ForeignKey("public.record_categories.id"))
    description: Mapped[Optional[text]]

    # Relationships
    record_categories: Mapped[list[RecordCategory]] = relationship(
        argument="RecordCategory",
        back_populates="record_types",
    )


class ResetToken(Base):
    __tablename__ = Relations.RESET_TOKENS.value

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("public.users.id"))
    token: Mapped[Optional[text]]
    create_date: Mapped[timestamp] = mapped_column(
        server_default=func.current_timestamp()
    )


class TestTable(Base):
    __tablename__ = Relations.TEST_TABLE.value

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    pet_name: Mapped[Optional[str_255]]
    species: Mapped[Optional[str_255]]


class User(Base):
    __tablename__ = Relations.USERS.value

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[Optional[timestamp_tz]]
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


class Permission(Base):
    __tablename__ = Relations.PERMISSIONS.value

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    permission_name: Mapped[str_255]
    description: Mapped[Optional[text]]


class UserPermission(Base):
    __tablename__ = Relations.USER_PERMISSIONS.value

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("public.users.id"))
    permission_id: Mapped[int] = mapped_column(ForeignKey("public.permissions.id"))


class PendingUser(Base):
    __tablename__ = Relations.PENDING_USERS.value

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[Optional[timestamp_tz]]
    email: Mapped[text] = mapped_column(unique=True)
    password_digest: Mapped[Optional[text]]
    validation_token: Mapped[Optional[text]]


class LinkLocationDataRequest(Base):
    __tablename__ = Relations.LINK_LOCATIONS_DATA_REQUESTS.value

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("public.locations.id"))
    data_request_id: Mapped[int] = mapped_column(ForeignKey("public.data_requests.id"))


class DependentLocation(Base):
    __tablename__ = Relations.DEPENDENT_LOCATIONS.value
    __mapper_args__ = {"primary_key": ["parent_location_id", "dependent_location_id"]}

    parent_location_id: Mapped[int] = mapped_column(ForeignKey("public.locations.id"))
    dependent_location_id: Mapped[int] = mapped_column(
        ForeignKey("public.locations.id")
    )


class DataRequestPendingEventNotification(Base):
    __tablename__ = Relations.DATA_REQUESTS_PENDING_EVENT_NOTIFICATIONS.value

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    data_request_id: Mapped[int] = mapped_column(ForeignKey("public.data_requests.id"))
    event_type: Mapped[EventTypeDataRequestLiteral] = mapped_column(
        Enum(*get_args(EventTypeDataRequestLiteral), name="event_type_data_request")
    )
    created_at: Mapped[timestamp] = mapped_column(
        server_default=func.current_timestamp()
    )

    # Relationships
    data_request = relationship(
        argument="DataRequest",
        primaryjoin="DataRequestPendingEventNotification.data_request_id == DataRequest.id",
        uselist=False,
    )


class DataSourcePendingEventNotification(Base):
    __tablename__ = Relations.DATA_SOURCES_PENDING_EVENT_NOTIFICATIONS.value

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    data_source_id: Mapped[int] = mapped_column(ForeignKey("public.data_sources.id"))
    event_type: Mapped[EventTypeDataSourceLiteral] = mapped_column(
        Enum(*get_args(EventTypeDataSourceLiteral), name="event_type_data_source")
    )
    created_at: Mapped[timestamp] = mapped_column(
        server_default=func.current_timestamp()
    )

    # Relationships
    data_source = relationship(
        argument="DataSource",
        primaryjoin="DataSourcePendingEventNotification.data_source_id == DataSource.id",
        uselist=False,
    )


class DataRequestUserNotificationQueue(Base):
    __tablename__ = Relations.DATA_REQUESTS_USER_NOTIFICATION_QUEUE.value

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(
        ForeignKey("public.data_request_pending_event_notification.id")
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("public.users.id"))
    sent_at: Mapped[Optional[timestamp]]

    # Relationships
    pending_event_notification = relationship(
        argument="DataRequestPendingEventNotification",
        primaryjoin="DataRequestUserNotificationQueue.event_id == DataRequestPendingEventNotification.id",
        uselist=False,
    )
    user = relationship(
        argument="User",
        primaryjoin="DataRequestUserNotificationQueue.user_id == User.id",
        uselist=False,
    )


class DataSourceUserNotificationQueue(Base):
    __tablename__ = Relations.DATA_SOURCES_USER_NOTIFICATION_QUEUE.value

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(
        ForeignKey("public.data_source_pending_event_notification.id")
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("public.users.id"))
    sent_at: Mapped[Optional[timestamp]]

    # Relationships
    pending_event_notification = relationship(
        argument="DataSourcePendingEventNotification",
        primaryjoin="DataSourceUserNotificationQueue.event_id == DataSourcePendingEventNotification.id",
        uselist=False,
    )
    user = relationship(
        argument="User",
        primaryjoin="DataSourceUserNotificationQueue.user_id == User.id",
        uselist=False,
    )


class RecentSearch(Base):
    __tablename__ = Relations.RECENT_SEARCHES.value

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("public.users.id"))
    location_id: Mapped[int] = mapped_column(ForeignKey("public.locations.id"))
    created_at: Mapped[timestamp] = mapped_column(
        server_default=func.current_timestamp()
    )


class LinkRecentSearchRecordCategories(Base):
    __tablename__ = Relations.LINK_RECENT_SEARCH_RECORD_CATEGORIES.value

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    recent_search_id: Mapped[int] = mapped_column(
        ForeignKey("public.recent_searches.id")
    )
    record_category_id: Mapped[int] = mapped_column(
        ForeignKey("public.record_categories.id")
    )


class LinkRecentSearchRecordTypes(Base):
    __tablename__ = Relations.LINK_RECENT_SEARCH_RECORD_TYPES.value

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    recent_search_id: Mapped[int] = mapped_column(
        ForeignKey("public.recent_searches.id")
    )
    record_type_id: Mapped[int] = mapped_column(ForeignKey("public.record_types.id"))


# TODO: Change user_id references in models to be from singular factory function or constant, to avoid duplication
# Do the same for other common foreign keys, or for things such as primary keys


class RecentSearchExpanded(Base, CountMetadata):
    __tablename__ = Relations.RECENT_SEARCHES_EXPANDED.value

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("public.users.id"))
    location_id: Mapped[int] = mapped_column(ForeignKey("public.locations.id"))
    state_name: Mapped[str]
    county_name: Mapped[str]
    locality_name: Mapped[str]
    location_type: Mapped[LocationTypeLiteral]
    record_categories = mapped_column(ARRAY(String, as_tuple=True))


class ChangeLog(Base):
    __tablename__ = Relations.CHANGE_LOG.value

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    operation_type: Mapped[OperationTypeLiteral]
    table_name: Mapped[str]
    affected_id: Mapped[int]
    old_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    new_data: Mapped[dict] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[timestamp] = mapped_column(
        server_default=func.current_timestamp()
    )


SQL_ALCHEMY_TABLE_REFERENCE = {
    "agencies": Agency,
    "agencies_expanded": AgencyExpanded,
    Relations.LINK_AGENCIES_DATA_SOURCES.value: LinkAgencyDataSource,
    Relations.LINK_LOCATIONS_DATA_REQUESTS.value: LinkLocationDataRequest,
    "data_requests": DataRequest,
    "data_requests_expanded": DataRequestExpanded,
    "data_sources": DataSource,
    "data_sources_expanded": DataSourceExpanded,
    "data_sources_archive_info": DataSourceArchiveInfo,
    "link_data_sources_data_requests": LinkDataSourceDataRequest,
    "reset_tokens": ResetToken,
    "test_table": TestTable,
    "users": User,
    "us_states": USState,
    "counties": County,
    "localities": Locality,
    "locations": Location,
    "locations_expanded": LocationExpanded,
    "link_user_followed_location": LinkUserFollowedLocation,
    "external_accounts": ExternalAccount,
    "data_requests_github_issue_info": DataRequestsGithubIssueInfo,
    Relations.DEPENDENT_LOCATIONS.value: DependentLocation,
    Relations.RECENT_SEARCHES.value: RecentSearch,
    Relations.LINK_RECENT_SEARCH_RECORD_CATEGORIES.value: LinkRecentSearchRecordCategories,
    Relations.LINK_RECENT_SEARCH_RECORD_TYPES.value: LinkRecentSearchRecordTypes,
    Relations.RECORD_CATEGORIES.value: RecordCategory,
    Relations.RECENT_SEARCHES_EXPANDED.value: RecentSearchExpanded,
    Relations.RECORD_TYPES.value: RecordType,
    Relations.PENDING_USERS.value: PendingUser,
    Relations.CHANGE_LOG.value: ChangeLog,
}


def convert_to_column_reference(columns: list[str], relation: str) -> list[Column]:
    """Converts a list of column strings to SQLAlchemy column references.

    :param columns: List of column strings.
    :param relation: Relation string.
    :return:
    """
    try:
        relation_reference = SQL_ALCHEMY_TABLE_REFERENCE[relation]
    except KeyError:
        raise ValueError(
            f"SQL Model does not exist in SQL_ALCHEMY_TABLE_REFERENCE: {relation}"
        )

    def get_attribute(column: str) -> Column:
        try:
            return getattr(relation_reference, column)
        except AttributeError:
            raise AttributeError(
                f'Column "{column}" does not exist in SQLAlchemy Table Model for "{relation}"'
            )

    return [get_attribute(column) for column in columns]
