# pyright: reportUninitializedInstanceVariable=false

from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from db.models.implementations.core.data_request.core import DataRequest
from db.models.types import text
from middleware.enums import Relations


class DataRequestExpanded(DataRequest):
    id = mapped_column(None, ForeignKey("public.data_requests.id"), primary_key=True)

    __tablename__ = Relations.DATA_REQUESTS_EXPANDED.value
    github_issue_url: Mapped[text | None]
    github_issue_number: Mapped[int | None]

    data_sources: Mapped[list["DataSourceExpanded"]] = relationship(
        argument="DataSourceExpanded",
        secondary="public.link_data_sources_data_requests",
        primaryjoin="DataRequestExpanded.id == LinkDataSourceDataRequest.request_id",
        secondaryjoin="DataSourceExpanded.id == LinkDataSourceDataRequest.data_source_id",
        back_populates="data_requests",
    )
