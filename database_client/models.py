from typing import Optional, Literal, get_args
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    Column,
    BigInteger,
    text,
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
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql.expression import false, func

from database_client.enums import LocationType
from middleware.enums import Relations

ExternalAccountType = Literal["github"]
RecordType = Literal[
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
RequestStatus = Literal[
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


class Base(DeclarativeBase):
    pass


PUBLIC_SCHEMA = {"schema": "public"}


class Agency(Base):
    __tablename__ = Relations.AGENCIES.value
    __table_args__ = PUBLIC_SCHEMA

    airtable_uid: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    submitted_name: Mapped[Optional[str]]
    homepage_url: Mapped[Optional[str]]
    jurisdiction_type: Mapped[Optional[str]]
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
    multi_agency: Mapped[Optional[bool]]
    zip_code: Mapped[Optional[str]]
    data_sources: Mapped[Optional[str]]
    no_web_presence: Mapped[Optional[bool]]
    airtable_agency_last_modified: Mapped[Optional[TIMESTAMP]] = mapped_column(
        TIMESTAMP(timezone=True)
    )
    data_sources_last_updated: Mapped[Optional[DATE]] = mapped_column(DATE)
    approved: Mapped[Optional[bool]]
    rejection_reason: Mapped[Optional[str]]
    last_approval_editor: Mapped[Optional[str]]
    submitter_contact: Mapped[Optional[str]]
    agency_created: Mapped[Optional[TIMESTAMP]] = mapped_column(
        TIMESTAMP(timezone=True)
    )
    county_airtable_uid: Mapped[Optional[str]]
    location_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("public.locations.id")
    )


class AgencyExpanded(Base):
    __tablename__ = Relations.AGENCIES_EXPANDED.value
    __table_args__ = PUBLIC_SCHEMA

    # Define columns as per the view with refined data types
    name = Column(String, nullable=False)
    submitted_name = Column(String)
    homepage_url = Column(String)
    jurisdiction_type = Column(String)
    state_iso = Column(String)
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
    __table_args__ = PUBLIC_SCHEMA

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    fips: Mapped[str] = mapped_column(Text)
    name: Mapped[Optional[Text]] = mapped_column(Text)
    name_ascii: Mapped[Optional[Text]] = mapped_column(Text)
    state_iso: Mapped[Optional[Text]] = mapped_column(Text)
    lat: Mapped[Optional[float]]
    lng: Mapped[Optional[float]]
    population: Mapped[Optional[int]]
    agencies: Mapped[Optional[Text]] = mapped_column(Text)
    airtable_uid: Mapped[Optional[Text]] = mapped_column(Text)
    airtable_county_last_modified: Mapped[Optional[Text]] = mapped_column(Text)
    airtable_county_created: Mapped[Optional[Text]] = mapped_column(Text)
    state_id: Mapped[int] = mapped_column(ForeignKey("public.us_states.id"))


class Locality(Base):
    __tablename__ = Relations.LOCALITIES.value
    __table_args__ = PUBLIC_SCHEMA

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[Optional[Text]] = mapped_column(Text)
    county_id: Mapped[int] = mapped_column(ForeignKey("public.counties.id"))


class Location(Base):
    __tablename__ = Relations.LOCATIONS.value
    __table_args__ = PUBLIC_SCHEMA

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    type: Mapped[Enum] = mapped_column(Enum(LocationType), nullable=False)
    state_id: Mapped[int] = mapped_column(
        ForeignKey("public.us_states.id"), nullable=False
    )
    county_id: Mapped[int] = mapped_column(ForeignKey("public.counties.id"))
    locality_id: Mapped[int] = mapped_column(ForeignKey("public.localities.id"))


class LocationExpanded(Base):
    __tablename__ = Relations.LOCATIONS_EXPANDED.value
    __table_args__ = {"schema": "public", "extend_existing": True}

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
    __table_args__ = PUBLIC_SCHEMA

    id: Mapped[int] = mapped_column(primary_key=True)
    state_iso: Mapped[str] = mapped_column(String(255), nullable=False)
    state_name: Mapped[str] = mapped_column(String(255))


class DataRequest(Base):
    __tablename__ = Relations.DATA_REQUESTS.value
    __table_args__ = PUBLIC_SCHEMA

    id: Mapped[int] = mapped_column(primary_key=True)
    submission_notes: Mapped[Optional[Text]] = mapped_column(Text)
    request_status: Mapped[RequestStatus] = mapped_column(
        Enum(*get_args(RequestStatus)), name="request_status", server_default="Intake"
    )
    submitter_email: Mapped[Optional[Text]] = mapped_column(Text)
    location_described_submitted: Mapped[Optional[Text]] = mapped_column(Text)
    archive_reason: Mapped[Optional[Text]] = mapped_column(Text)
    date_created: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()")
    )
    date_status_last_changed: Mapped[Optional[TIMESTAMP]] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()")
    )
    creator_user_id: Mapped[Optional[int]]
    github_issue_url: Mapped[Optional[Text]] = mapped_column(Text)
    internal_notes: Mapped[Optional[Text]] = mapped_column(Text)
    record_types_required: Mapped[Optional[ARRAY[RecordType]]] = mapped_column(
        ARRAY(Enum(*get_args(RecordType), name="record_type"))
    )
    pdap_response: Mapped[Optional[Text]] = mapped_column(Text)
    coverage_range: Mapped[Optional[DATERANGE]] = mapped_column(DATERANGE)
    data_requirements: Mapped[Optional[Text]] = mapped_column(Text)
    withdrawn: Mapped[Optional[bool]] = mapped_column(server_default=false())


class DataSource(Base):
    __tablename__ = Relations.DATA_SOURCES.value
    __table_args__ = PUBLIC_SCHEMA

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
    coverage_start: Mapped[Optional[DATE]] = mapped_column(DATE)
    coverage_end: Mapped[Optional[DATE]] = mapped_column(DATE)
    source_last_updated: Mapped[Optional[DATE]] = mapped_column(DATE)
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
    data_source_created: Mapped[Optional[TIMESTAMP]] = mapped_column(
        TIMESTAMP(timezone=True)
    )
    airtable_source_last_modified: Mapped[Optional[TIMESTAMP]] = mapped_column(
        TIMESTAMP(timezone=True)
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
    broken_source_url_as_of: Mapped[Optional[DATE]] = mapped_column(DATE)
    access_notes: Mapped[Optional[Text]] = mapped_column(Text)
    url_status: Mapped[Optional[Text]] = mapped_column(Text)
    approval_status: Mapped[Optional[Text]] = mapped_column(Text)
    record_type_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("public.record_types.id")
    )


class DataSourceArchiveInfo(Base):
    __tablename__ = Relations.DATA_SOURCES_ARCHIVE_INFO.value
    __table_args__ = PUBLIC_SCHEMA

    airtable_uid: Mapped[str] = mapped_column(
        ForeignKey("public.data_sources.airtable_uid"), primary_key=True
    )
    update_frequency: Mapped[Optional[str]]
    last_cached: Mapped[Optional[TIMESTAMP]] = mapped_column(TIMESTAMP)
    next_cached: Mapped[Optional[TIMESTAMP]] = mapped_column(TIMESTAMP)


class ExternalAccount(Base):
    __tablename__ = Relations.EXTERNAL_ACCOUNTS.value
    __table_args__ = PUBLIC_SCHEMA

    row_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("public.users.id"))
    account_type: Mapped[ExternalAccountType] = mapped_column(
        Enum(*get_args(ExternalAccountType)), name="account_type"
    )
    account_identifier: Mapped[str] = mapped_column(String(255))
    linked_at: Mapped[Optional[TIMESTAMP]] = mapped_column(
        TIMESTAMP, server_default=text("now()")
    )


class LinkDataSourceDataRequest(Base):
    __tablename__ = Relations.LINK_DATA_SOURCES_DATA_REQUESTS.value
    __table_args__ = PUBLIC_SCHEMA

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_id: Mapped[Text] = mapped_column(
        Text, ForeignKey("public.data_sources.airtable_uid")
    )
    request_id: Mapped[int] = mapped_column(ForeignKey("public.data_requests.id"))


class RecordCategory(Base):
    __tablename__ = Relations.RECORD_CATEGORIES.value
    __table_args__ = PUBLIC_SCHEMA

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[Text]] = mapped_column(Text)


class RecordType(Base):
    __tablename__ = Relations.RECORD_TYPES.value
    __table_args__ = PUBLIC_SCHEMA

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    category_id: Mapped[int] = mapped_column(ForeignKey("public.record_categories.id"))
    description: Mapped[Optional[Text]] = mapped_column(Text)


class ResetToken(Base):
    __tablename__ = Relations.RESET_TOKENS.value
    __table_args__ = PUBLIC_SCHEMA

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[Optional[Text]] = mapped_column(Text)
    token: Mapped[Optional[Text]] = mapped_column(Text)
    create_date: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )


class TestTable(Base):
    __tablename__ = Relations.TEST_TABLE.value
    __table_args__ = PUBLIC_SCHEMA

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    pet_name: Mapped[Optional[str]] = mapped_column(String(255))
    species: Mapped[Optional[str]] = mapped_column(String(255))


class User(Base):
    __tablename__ = Relations.USERS.value
    __table_args__ = PUBLIC_SCHEMA

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[Optional[TIMESTAMP]] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()")
    )
    updated_at: Mapped[Optional[TIMESTAMP]] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()")
    )
    email: Mapped[Text] = mapped_column(Text, unique=True)
    password_digest: Mapped[Optional[Text]] = mapped_column(Text)
    api_key: Mapped[Optional[str]] = mapped_column(
        server_default=text("generate_api_key()")
    )
    role: Mapped[Optional[Text]] = mapped_column(Text)
