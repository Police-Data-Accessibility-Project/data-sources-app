from datetime import datetime, date
from typing import Optional, Literal, get_args
from typing_extensions import Annotated

from sqlalchemy import (
    Column,
    BigInteger,
    text as text_func,
    Text,
    String,
    ForeignKey,
    Enum,
    Float,
    Boolean,
    DateTime,
    Integer,
)
from sqlalchemy.dialects.postgresql import ARRAY, DATE, DATERANGE, TIMESTAMP
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.sql.expression import false, func

from database_client.enums import LocationType
from middleware.enums import Relations


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
JurisdictionTypeLiteral = Literal[
    "federal", "state", "county", "local", "port", "tribal", "transit", "school"
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


class AgencySourceLink(Base):
    __tablename__ = "agency_source_link"

    link_id: Mapped[int]
    data_source_uid: Mapped[str] = mapped_column(
        ForeignKey("public.data_sources.airtable_uid"), primary_key=True
    )
    agency_uid: Mapped[str] = mapped_column(
        ForeignKey("public.agencies.airtable_uid"), primary_key=True
    )


class Agency(Base):
    __tablename__ = Relations.AGENCIES.value

    def __iter__(self):
        for key in self.__dict__:
            if key == "_sa_instance_state":
                continue
            else:
                value = getattr(self, key)
                value = (
                    str(value)
                    if type(value) == datetime or type(value) == date
                    else value
                )
                yield key, value

    airtable_uid: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    submitted_name: Mapped[Optional[str]]
    homepage_url: Mapped[Optional[str]]
    jurisdiction_type: Mapped[JurisdictionTypeLiteral]
    state_iso: Mapped[Optional[str]]
    municipality: Mapped[Optional[str]]
    county_fips: Mapped[Optional[str]] = mapped_column(
        ForeignKey("public.counties.fips")
    )
    county_name: Mapped[Optional[str]]
    lat: Mapped[Optional[float]]
    lng: Mapped[Optional[float]]
    defunct_year: Mapped[Optional[str]]
    count_data_sources: Mapped[Optional[int]]
    agency_type: Mapped[Optional[str]]
    multi_agency: Mapped[bool] = mapped_column(server_default=false())
    zip_code: Mapped[Optional[str]]
    data_sources: Mapped[Optional[str]]
    no_web_presence: Mapped[bool] = mapped_column(server_default=false())
    airtable_agency_last_modified: Mapped[timestamp_tz] = mapped_column(
        server_default=func.current_timestamp()
    )
    data_sources_last_updated: Mapped[Optional[date]]
    approved: Mapped[bool] = mapped_column(server_default=false())
    rejection_reason: Mapped[Optional[str]]
    last_approval_editor: Mapped[Optional[str]]
    submitter_contact: Mapped[Optional[str]]
    agency_created: Mapped[timestamp_tz] = mapped_column(
        server_default=func.current_timestamp()
    )
    county_airtable_uid: Mapped[Optional[str]]
    location_id: Mapped[Optional[int]]


class AgencyExpanded(Base):
    __tablename__ = Relations.AGENCIES_EXPANDED.value

    # Define columns as per the view with refined data types
    name = Column(String, nullable=False)
    submitted_name = Column(String)
    homepage_url = Column(String)
    jurisdiction_type: Mapped[JurisdictionTypeLiteral] = mapped_column(
        Enum(*get_args(JurisdictionTypeLiteral)), name="jurisdiction_type"
    )
    state_iso = Column(String)
    state_name = Column(String)
    county_fips = Column(String)  # Matches the VARCHAR type in the agencies table
    county_name = Column(String)
    lat = Column(Float)
    lng = Column(Float)
    defunct_year = Column(String)
    airtable_uid = Column(String, primary_key=True)  # Primary key
    count_data_sources = Column(
        BigInteger
    )  # Matches the BIGINT type in the agencies table
    agency_type = Column(String)
    multi_agency = Column(Boolean)
    zip_code = Column(String)
    data_sources = Column(String)  # Assuming 'data_sources' is a VARCHAR field
    no_web_presence = Column(Boolean)
    airtable_agency_last_modified = Column(DateTime(timezone=True))
    data_sources_last_updated = Column(DateTime)
    approved = Column(Boolean)
    rejection_reason = Column(String)
    last_approval_editor = Column(String)
    submitter_contact = Column(String)
    agency_created = Column(DateTime(timezone=True))
    county_airtable_uid = Column(String)
    locality_id = Column(BigInteger)
    locality_name = Column(String)


class County(Base):
    __tablename__ = Relations.COUNTIES.value

    id: Mapped[int] = mapped_column(primary_key=True)
    fips: Mapped[str]
    name: Mapped[Optional[text]]
    name_ascii: Mapped[Optional[text]]
    state_iso: Mapped[Optional[text]]
    lat: Mapped[Optional[float]]
    lng: Mapped[Optional[float]]
    population: Mapped[Optional[int]]
    agencies: Mapped[Optional[text]]
    airtable_uid: Mapped[Optional[text]]
    airtable_county_last_modified: Mapped[Optional[text]]
    airtable_county_created: Mapped[Optional[text]]
    state_id: Mapped[Optional[int]]


class Locality(Base):
    __tablename__ = Relations.LOCALITIES.value

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[Optional[Text]] = mapped_column(Text)
    county_id: Mapped[int] = mapped_column(ForeignKey("public.counties.id"))


class Location(Base):
    __tablename__ = Relations.LOCATIONS.value

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    type: Mapped[Enum] = mapped_column(Enum(LocationType), nullable=False)
    state_id: Mapped[int] = mapped_column(
        ForeignKey("public.us_states.id"), nullable=False
    )
    county_id: Mapped[int] = mapped_column(ForeignKey("public.counties.id"))
    locality_id: Mapped[int] = mapped_column(ForeignKey("public.localities.id"))


class LocationExpanded(Base):
    __tablename__ = Relations.LOCATIONS_EXPANDED.value
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
    type = Column(
        Enum(LocationType)
    )  # Adjust the type if 'type' is more specific, like Enum or similar.
    state_name = Column(String)
    state_iso = Column(String)
    county_name = Column(String)
    county_fips = Column(String)
    locality_name = Column(String)
    state_id = Column(Integer)
    county_id = Column(Integer)
    locality_id = Column(Integer)


class USState(Base):
    __tablename__ = Relations.US_STATES.value

    id: Mapped[int] = mapped_column(primary_key=True)
    state_iso: Mapped[str] = mapped_column(String(255), nullable=False)
    state_name: Mapped[str] = mapped_column(String(255))


class DataRequest(Base):
    __tablename__ = Relations.DATA_REQUESTS.value

    id: Mapped[int] = mapped_column(primary_key=True)
    submission_notes: Mapped[Optional[text]]
    request_status: Mapped[RequestStatusLiteral] = mapped_column(
        server_default="Intake"
    )
    location_described_submitted: Mapped[Optional[text]]
    archive_reason: Mapped[Optional[text]]
    date_created: Mapped[timestamp_tz]
    date_status_last_changed: Mapped[Optional[timestamp_tz]]
    creator_user_id: Mapped[Optional[int]]
    github_issue_url: Mapped[Optional[text]]
    internal_notes: Mapped[Optional[text]]
    record_types_required: Mapped[Optional[ARRAY[RecordTypeLiteral]]] = mapped_column(
        ARRAY(Enum(*get_args(RecordTypeLiteral), name="record_type"), as_tuple=True)
    )
    pdap_response: Mapped[Optional[text]]
    coverage_range: Mapped[Optional[daterange]]
    data_requirements: Mapped[Optional[text]]


class DataSource(Base):
    __tablename__ = Relations.DATA_SOURCES.value

    def __iter__(self):
        for key in self.__dict__:
            match key:
                case "_sa_instance_state":
                    continue
                case "airtable_uid":
                    yield key, self.airtable_uid
                    yield "agency_ids", self.agency_ids
                case "agencies":
                    yield key, [dict(agency) for agency in self.agencies]
                case _:
                    value = getattr(self, key)
                    value = str(value) if type(value) == datetime else value
                    yield key, value

    airtable_uid: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    submitted_name: Mapped[Optional[str]]
    description: Mapped[Optional[str]]
    record_type: Mapped[Optional[str]]
    source_url: Mapped[Optional[str]]
    agency_supplied: Mapped[Optional[bool]]
    supplying_entity: Mapped[Optional[str]]
    agency_originated: Mapped[Optional[bool]]
    agency_aggregation: Mapped[Optional[str]]
    coverage_start: Mapped[Optional[date]]
    coverage_end: Mapped[Optional[date]]
    source_last_updated: Mapped[Optional[date]]
    detail_level: Mapped[Optional[str]]
    number_of_records_available: Mapped[Optional[int]]
    size: Mapped[Optional[str]]
    access_type: Mapped[Optional[str]]
    record_download_option_provided: Mapped[Optional[bool]]
    data_portal_type: Mapped[Optional[str]]
    record_format: Mapped[Optional[str]]
    update_method: Mapped[Optional[str]]
    tags: Mapped[Optional[str]]
    readme_url: Mapped[Optional[str]]
    originating_entity: Mapped[Optional[str]]
    retention_schedule: Mapped[Optional[str]]
    scraper_url: Mapped[Optional[str]]
    data_source_created: Mapped[Optional[timestamp_tz]] = mapped_column(
        server_default=None
    )
    airtable_source_last_modified: Mapped[Optional[timestamp_tz]] = mapped_column(
        server_default=None
    )
    url_broken: Mapped[Optional[bool]]
    submission_notes: Mapped[Optional[str]]
    rejection_note: Mapped[Optional[str]]
    last_approval_editor: Mapped[Optional[str]]
    submitter_contact_info: Mapped[Optional[str]]
    agency_described_submitted: Mapped[Optional[str]]
    agency_described_not_in_database: Mapped[Optional[str]]
    approved: Mapped[Optional[bool]]
    record_type_other: Mapped[Optional[str]]
    data_portal_type_other: Mapped[Optional[str]]
    private_access_instructions: Mapped[Optional[str]]
    records_not_online: Mapped[Optional[bool]]
    data_source_request: Mapped[Optional[str]]
    url_button: Mapped[Optional[str]]
    tags_other: Mapped[Optional[str]]
    broken_source_url_as_of: Mapped[Optional[date]]
    access_notes: Mapped[Optional[text]]
    url_status: Mapped[Optional[text]]
    approval_status: Mapped[Optional[text]]
    record_type_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("public.record_types.id")
    )

    agencies: Mapped[list[Agency]] = relationship(
        secondary="public.agency_source_link",
        lazy="joined",
        innerjoin=True,
    )

    @hybrid_property
    def agency_ids(self) -> list[str]:
        return [agency.airtable_uid for agency in self.agencies]


class DataSourceArchiveInfo(Base):
    __tablename__ = Relations.DATA_SOURCES_ARCHIVE_INFO.value

    airtable_uid: Mapped[str] = mapped_column(
        ForeignKey("public.data_sources.airtable_uid"), primary_key=True
    )
    update_frequency: Mapped[Optional[str]]
    last_cached: Mapped[Optional[timestamp]]
    next_cached: Mapped[Optional[timestamp]]


class ExternalAccount(Base):
    __tablename__ = Relations.EXTERNAL_ACCOUNTS.value

    row_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("public.users.id"))
    account_type: Mapped[ExternalAccountTypeLiteral]
    account_identifier: Mapped[str_255]
    linked_at: Mapped[Optional[timestamp]] = mapped_column(server_default=func.now())


class LinkDataSourceDataRequest(Base):
    __tablename__ = Relations.LINK_DATA_SOURCES_DATA_REQUESTS.value

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_id: Mapped[text] = mapped_column(
        ForeignKey("public.data_sources.airtable_uid")
    )
    request_id: Mapped[int] = mapped_column(ForeignKey("public.data_requests.id"))


class LinkUserFollowedLocation(Base):
    __tablename__ = Relations.LINK_USER_FOLLOWED_LOCATION.value

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("public.users.id"))
    location_id: Mapped[int] = mapped_column(ForeignKey("public.locations.id"))


class RecordCategory(Base):
    __tablename__ = Relations.RECORD_CATEGORIES.value

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str_255]
    description: Mapped[Optional[text]]


class RecordType(Base):
    __tablename__ = Relations.RECORD_TYPES.value

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str_255]
    category_id: Mapped[int] = mapped_column(ForeignKey("public.record_categories.id"))
    description: Mapped[Optional[text]]


class ResetToken(Base):
    __tablename__ = Relations.RESET_TOKENS.value

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[Optional[text]]
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


SQL_ALCHEMY_TABLE_REFERENCE = {
    "agencies": Agency,
    "agencies_expanded": AgencyExpanded,
    "data_requests": DataRequest,
    "data_sources": DataSource,
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
            pass

    return [get_attribute(column) for column in columns]
