# pyright: reportUninitializedInstanceVariable=false
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from db.models.implementations.core.agency.core import Agency
from db.models.implementations.core.data_request.expanded import DataRequestExpanded
from db.models.implementations.core.data_source.core import DataSource
from middleware.enums import Relations


class DataSourceExpanded(DataSource):
    id = mapped_column(None, ForeignKey("public.data_sources.id"), primary_key=True)

    __tablename__ = Relations.DATA_SOURCES_EXPANDED.value

    record_type_name: Mapped[str | None]

    agencies: Mapped[list[Agency]] = relationship(
        argument="Agency",
        secondary="public.link_agencies_data_sources",
        primaryjoin="LinkAgencyDataSource.data_source_id == DataSourceExpanded.id",
        secondaryjoin="LinkAgencyDataSource.agency_id == Agency.id",
        back_populates="data_sources",
    )

    data_requests: Mapped[list[DataRequestExpanded]] = relationship(
        argument="DataRequestExpanded",
        secondary="public.link_data_sources_data_requests",
        primaryjoin="LinkDataSourceDataRequest.data_source_id == DataSourceExpanded.id",
        secondaryjoin="LinkDataSourceDataRequest.request_id == DataRequestExpanded.id",
        back_populates="data_sources",
    )
