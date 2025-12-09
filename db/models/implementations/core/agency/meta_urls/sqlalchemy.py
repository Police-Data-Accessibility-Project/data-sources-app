from sqlalchemy.orm import Mapped, mapped_column

from db.enums import URLStatus
from db.models.helpers import enum_column
from db.models.mixins import CreatedAtMixin, UpdatedAtMixin
from db.models.templates.standard import StandardBase


class MetaURL(
    StandardBase,
    UpdatedAtMixin,
    CreatedAtMixin,
):
    __tablename__ = "meta_urls"

    url: Mapped[str] = mapped_column()
    internet_archive_url: Mapped[str | None] = mapped_column()
    url_status: Mapped[str] = enum_column(
        enum=URLStatus,
        name="url_status_enum",
        default=URLStatus.OK,
    )
