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
)
from sqlalchemy.dialects.postgresql import DATE, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


ExternalAccountType = Literal["github"]


class Base(DeclarativeBase):
    pass


class Agency(Base):
    __tablename__ = "agencies"
    __table_args__ = {"schema": "public"}

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


class County(Base):
    __tablename__ = "counties"
    __table_args__ = {"schema": "public"}

    fips: Mapped[str] = mapped_column(primary_key=True)
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


class DataSource(Base):
    __tablename__ = "data_sources"
    __table_args__ = {"schema": "public"}

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
    rejection_notes: Mapped[Optional[str]]
    last_approval_editor: Mapped[Optional[str]]
    submitter_contact_info: Mapped[Optional[str]]
    agency_described_submitted: Mapped[Optional[str]]
    agency_described_not_in_database: Mapped[Optional[str]]
    approval: Mapped[Optional[bool]]
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


class ExternalAccount(Base):
    __tablename__ = "external_accounts"
    __table_args__ = {"schema": "public"}

    row_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("public.users.id"))
    account_type: Mapped[ExternalAccountType] = mapped_column(
        Enum(*get_args(ExternalAccountType)), name="account_type"
    )
    account_identifier: Mapped[str] = mapped_column(String(255))
    linked_at: Mapped[Optional[TIMESTAMP]] = mapped_column(
        TIMESTAMP, server_default=text("now()")
    )


class TestTable(Base):
    __tablename__ = "test_table"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    pet_name: Mapped[Optional[str]] = mapped_column(String(255))
    species: Mapped[Optional[str]] = mapped_column(String(255))


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "public"}

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
