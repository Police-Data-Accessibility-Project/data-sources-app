from sqlalchemy.orm import Mapped, mapped_column

from db.models.mixins import CreatedAtMixin, UpdatedAtMixin
from db.models.templates.standard import StandardBase


class MetaURL(
    StandardBase,
    UpdatedAtMixin,
    CreatedAtMixin,
):
    __tablename__ = "meta_urls"

    url: Mapped[str] = mapped_column()
