# pyright: reportUninitializedInstanceVariable=false

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from db.models.mixins import UserIDMixin
from db.models.templates.standard import StandardBase
from db.models.types import timestamp
from middleware.enums import Relations


class ResetToken(StandardBase, UserIDMixin):
    __tablename__ = Relations.RESET_TOKENS.value

    token: Mapped[str | None]
    create_date: Mapped[timestamp] = mapped_column(
        server_default=func.current_timestamp()
    )
