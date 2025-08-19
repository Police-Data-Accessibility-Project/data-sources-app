from sqlalchemy.orm import Mapped

from db.models.mixins import CreatedAtMixin, UpdatedAtMixin, AgencyIDMixin
from db.models.templates.standard import StandardBase


class AgencyMetaURL(
    StandardBase,
    UpdatedAtMixin,
    CreatedAtMixin,
    AgencyIDMixin,
):

    __tablename__ = "agency_meta_urls"

    url: Mapped[str]