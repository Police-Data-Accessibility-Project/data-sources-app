from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base
from db.models.mixins import UserIDMixin
from db.models.types import ExternalAccountTypeLiteral, str_255, timestamp
from middleware.enums import Relations


class ExternalAccount(Base, UserIDMixin):
    __tablename__ = Relations.EXTERNAL_ACCOUNTS.value
    row_id: Mapped[int] = mapped_column(primary_key=True)
    account_type: Mapped[ExternalAccountTypeLiteral]
    account_identifier: Mapped[str_255]
    linked_at: Mapped[Optional[timestamp]] = mapped_column(server_default=func.now())
