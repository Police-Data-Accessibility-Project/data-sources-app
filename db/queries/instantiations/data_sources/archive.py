from collections import namedtuple
from datetime import datetime
from typing import Optional

from sqlalchemy import or_, select

from db.constants import PAGE_SIZE
from db.enums import UpdateFrequency, URLStatus
from db.helpers import get_offset
from db.models.implementations.core.data_source.archive import DataSourceArchiveInfo
from db.models.implementations.core.data_source.core import DataSource
from db.queries.builder.core import QueryBuilderBase

ArchiveInfo = namedtuple(
    "ArchiveInfo",
    ["id", "url", "update_frequency", "last_cached", "broken_url_as_of"],
)


class GetDataSourcesToArchiveQueryBuilder(QueryBuilderBase):
    """
    Pulls data sources to be archived by the automatic archives script.

    A data source is selected for archival if:
    The data source has been approved
    AND (
        the data source has not been archived previously
        OR the data source is updated regularly
    )
    AND the source url is not broken
    AND the source url is not null.

    :return: A list of ArchiveInfo named tuples, each containing archive details of a data source.
    """

    def __init__(
        self,
        update_frequency: Optional[UpdateFrequency] = None,
        last_archived_before: Optional[datetime] = None,
        page: int = 1,
    ):
        super().__init__()
        self.update_frequency = update_frequency
        self.last_archived_before = last_archived_before
        self.page = page

    def run(self) -> list[ArchiveInfo]:
        def get_where_queries():
            clauses = [
                or_(
                    DataSourceArchiveInfo.last_cached.is_(None),
                    DataSourceArchiveInfo.update_frequency.isnot(None),
                ),
                DataSource.url_status != URLStatus.BROKEN.value,
                DataSource.source_url.isnot(None),
            ]
            if self.update_frequency is not None:
                clauses.append(
                    DataSourceArchiveInfo.update_frequency
                    == self.update_frequency.value
                )
            if self.last_archived_before is not None:
                clauses.append(
                    DataSourceArchiveInfo.last_cached < self.last_archived_before
                )
            return clauses

        query = (
            select(
                DataSource.id,
                DataSource.source_url,
                DataSourceArchiveInfo.update_frequency,
                DataSourceArchiveInfo.last_cached,
                DataSource.broken_source_url_as_of,
            )
            .select_from(DataSource)
            .join(
                DataSourceArchiveInfo,
                DataSource.id == DataSourceArchiveInfo.data_source_id,
            )
            .where(*get_where_queries())
            .limit(PAGE_SIZE)
            .offset(get_offset(self.page))
        )

        data_sources = self.session.execute(query).mappings().all()

        results = [
            ArchiveInfo(
                id=row["id"],
                url=row["source_url"],
                update_frequency=row["update_frequency"],
                last_cached=row["last_cached"],
                broken_url_as_of=row["broken_source_url_as_of"],
            )
            for row in data_sources
        ]

        return results
