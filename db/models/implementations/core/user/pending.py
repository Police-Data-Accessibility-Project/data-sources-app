from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column

from db.models.mixins import CreatedAtMixin
from db.models.templates.standard import StandardBase
from db.models.types import text
from middleware.enums import Relations


class PendingUser(StandardBase, CreatedAtMixin):
    __tablename__ = Relations.PENDING_USERS.value

    email: Mapped[str] = mapped_column(unique=True)
    password_digest: Mapped[Optional[str]]
    validation_token: Mapped[Optional[str]]
