from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base
from middleware.enums import Relations


class DistinctSourceURL(Base):
    __tablename__ = Relations.DISTINCT_SOURCE_URLS.value

    base_url: Mapped[str] = mapped_column(primary_key=True)
    original_url: Mapped[str]
    rejection_note: Mapped[str]
    approval_status: Mapped[str]
