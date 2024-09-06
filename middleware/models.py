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
