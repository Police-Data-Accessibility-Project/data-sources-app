from enums import ExternalAccountTypeEnum
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    Column,
    BigInteger,
    text,
    Text,
    String,
    Integer,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import TIMESTAMP

db = SQLAlchemy()

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "public"}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    email = Column(Text, nullable=False, unique=True)
    password_digest = Column(Text)
    api_key = Column(String)
    role = Column(Text)


class ExternalAccount(Base):
    __tablename__ = "external_accounts"
    __table_args__ = {"schema": "public"}

    row_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    account_type = Column(ExternalAccountTypeEnum, nullable=False)
    account_identifier = Column(String(255), nullable=False)
    linked_at = Column(TIMESTAMP, server_default=text("now()"))
