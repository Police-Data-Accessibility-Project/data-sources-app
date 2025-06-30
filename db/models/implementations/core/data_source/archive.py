# pyright: reportUninitializedInstanceVariable=false

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base
from db.models.types import timestamp
from middleware.enums import Relations


class DataSourceArchiveInfo(Base):
    __tablename__ = Relations.DATA_SOURCES_ARCHIVE_INFO.value

    data_source_id: Mapped[str] = mapped_column(
        ForeignKey("public.data_sources.id"), primary_key=True
    )
    update_frequency: Mapped[str | None]
    last_cached: Mapped[timestamp | None]
    next_cached: Mapped[timestamp | None]
