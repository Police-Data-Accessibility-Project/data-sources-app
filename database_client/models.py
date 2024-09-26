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
)
from sqlalchemy.dialects.postgresql import ARRAY, DATE, DATERANGE, TIMESTAMP
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import (
    DeclarativeBase,
    join,
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.sql.expression import false, func


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
JurisdictionType = Literal[
    "school",
    "county",
    "local",
    "port",
    "tribal",
    "transit",
    "state",
    "federal",
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
    __tablename__ = "agencies"

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
    jurisdiction_type: Mapped[JurisdictionType]
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


class County(Base):
    __tablename__ = "counties"

    fips: Mapped[str] = mapped_column(primary_key=True)
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


class DataRequest(Base):
    __tablename__ = "data_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    submission_notes: Mapped[Optional[text]]
    request_status: Mapped[RequestStatus] = mapped_column(server_default="Intake")
    submitter_email: Mapped[Optional[text]]
    location_described_submitted: Mapped[Optional[text]]
    archive_reason: Mapped[Optional[text]]
    date_created: Mapped[timestamp_tz]
    date_status_last_changed: Mapped[Optional[timestamp_tz]]
    creator_user_id: Mapped[Optional[int]]
    github_issue_url: Mapped[Optional[text]]
    internal_notes: Mapped[Optional[text]]
    record_types_required: Mapped[Optional[ARRAY[RecordType]]] = mapped_column(
        ARRAY(Enum(*get_args(RecordType), name="record_type"))
    )
    pdap_response: Mapped[Optional[text]]
    coverage_range: Mapped[Optional[daterange]]
    data_requirements: Mapped[Optional[text]]
    withdrawn: Mapped[Optional[bool]] = mapped_column(server_default=false())


class DataSource(Base):
    __tablename__ = "data_sources"

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
    __tablename__ = "data_sources_archive_info"

    airtable_uid: Mapped[str] = mapped_column(
        ForeignKey("public.data_sources.airtable_uid"), primary_key=True
    )
    update_frequency: Mapped[Optional[str]]
    last_cached: Mapped[Optional[timestamp]]
    next_cached: Mapped[Optional[timestamp]]


class ExternalAccount(Base):
    __tablename__ = "external_accounts"
    __table_args__ = {"schema": "public"}

    row_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("public.users.id"))
    account_type: Mapped[ExternalAccountType]
    account_identifier: Mapped[str_255]
    linked_at: Mapped[Optional[timestamp]] = mapped_column(server_default=func.now())


class LinkDataSourceDataRequest(Base):
    __tablename__ = "link_data_sources_data_requests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_id: Mapped[text] = mapped_column(
        ForeignKey("public.data_sources.airtable_uid")
    )
    request_id: Mapped[int] = mapped_column(ForeignKey("public.data_requests.id"))


class RecordCategory(Base):
    __tablename__ = "record_categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str_255]
    description: Mapped[Optional[text]]


class RecordType(Base):
    __tablename__ = "record_types"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str_255]
    category_id: Mapped[int] = mapped_column(ForeignKey("public.record_categories.id"))
    description: Mapped[Optional[text]]


class ResetToken(Base):
    __tablename__ = "reset_tokens"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[Optional[text]]
    token: Mapped[Optional[text]]
    create_date: Mapped[timestamp] = mapped_column(
        server_default=func.current_timestamp()
    )


class TestTable(Base):
    __tablename__ = "test_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    pet_name: Mapped[Optional[str_255]]
    species: Mapped[Optional[str_255]]


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[Optional[timestamp_tz]]
    updated_at: Mapped[Optional[timestamp_tz]]
    email: Mapped[text] = mapped_column(unique=True)
    password_digest: Mapped[Optional[text]]
    api_key: Mapped[Optional[str]] = mapped_column(
        server_default=text_func("generate_api_key()")
    )
    role: Mapped[Optional[text]]


TABLE_REFERENCE = {
    "agencies": Agency,
    "data_requests": DataRequest,
    "data_sources": DataSource,
    "data_sources_archive_info": DataSourceArchiveInfo,
    "link_data_sources_data_requests": LinkDataSourceDataRequest,
    "reset_tokens": ResetToken,
    "test_table": TestTable,
    "users": User,
}


def convert_to_column_reference(columns: list[str], relation: str) -> list[Column]:
    """Converts a list of column strings to SQLAlchemy column references.

    :param columns: List of column strings.
    :param relation: Relation string.
    :return:
    """
    relation_reference = TABLE_REFERENCE[relation]
    return [getattr(relation_reference, column) for column in columns]
