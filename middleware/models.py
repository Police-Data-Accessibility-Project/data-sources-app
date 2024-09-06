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
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import TIMESTAMP

db = SQLAlchemy()

ExternalAccountType = Literal["github"]


class Base(DeclarativeBase):
    pass


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

    id: Mapped[BigInteger] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    pet_name: Mapped[Optional[str]] = mapped_column(String(255))
    species: Mapped[Optional[str]] = mapped_column(String(255))


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "public"}

    id: Mapped[BigInteger] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    created_at: Mapped[Optional[TIMESTAMP]] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()")
    )
    updated_at: Mapped[Optional[TIMESTAMP]] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()")
    )
    email: Mapped[Text] = mapped_column(Text, unique=True)
    password_digest: Mapped[Optional[Text]] = mapped_column(Text)
    api_key: Mapped[Optional[str]] = mapped_column(server_default=text("generate_api_key()"))
    role: Mapped[Optional[Text]] = mapped_column(Text)

