# pyright: reportUninitializedInstanceVariable=false
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column

from db.models.mixins import CreatedAtMixin
from db.models.templates.standard import StandardBase
from middleware.enums import Relations


class PendingUser(StandardBase, CreatedAtMixin):
    __tablename__ = Relations.PENDING_USERS.value

    email: Mapped[str] = mapped_column(unique=True)
    password_digest: Mapped[str | None]
    validation_token: Mapped[str | None]
