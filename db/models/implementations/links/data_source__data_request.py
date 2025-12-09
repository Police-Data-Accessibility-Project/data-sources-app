from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from db.models.mixins import DataSourceIDMixin
from db.models.templates.standard import StandardBase
from middleware.enums import Relations


class LinkDataSourceDataRequest(StandardBase, DataSourceIDMixin):
    __tablename__ = Relations.LINK_DATA_SOURCES_DATA_REQUESTS.value

    request_id: Mapped[int] = mapped_column(ForeignKey("public.data_requests.id"))
