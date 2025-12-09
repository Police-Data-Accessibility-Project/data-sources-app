from typing import Sequence

from sqlalchemy import select, RowMapping, func, delete

from db.models.implementations import LinkAgencyMetaURL
from db.models.implementations.links.agency__data_source import LinkAgencyDataSource
from db.models.implementations.core.agency.core import Agency
from db.queries.builder.core import QueryBuilderBase
from endpoints.v3.source_manager.sync.agencies.delete.exceptions import (
    OrphanedEntityException,
)
from endpoints.v3.source_manager.sync.shared.models.request.delete import (
    SourceManagerDeleteRequest,
)


class SourceManagerDeleteAgenciesQueryBuilder(QueryBuilderBase):
    def __init__(self, request: SourceManagerDeleteRequest):
        super().__init__()
        self.request = request

    def run(self) -> None:
        self.check_for_no_meta_url_orphans()
        self.check_for_no_data_source_orphans()

        # Delete the agencies.
        statement = delete(Agency).where(Agency.id.in_(self.request.ids))

        self.execute(statement)

    def check_for_no_meta_url_orphans(self) -> None:
        """
        Check that no meta URLs would be orphaned by this process
        If they would, raise error
        """

        query = select(
            LinkAgencyMetaURL.meta_url_id,
            LinkAgencyMetaURL.agency_id,
        ).where(LinkAgencyMetaURL.agency_id.in_(self.request.ids))
        mappings: Sequence[RowMapping] = self.mappings(query)
        potential_orphan_mappings: list[dict[str, int]] = []
        for mapping in mappings:
            pom = {
                "meta_url_id": mapping[LinkAgencyMetaURL.meta_url_id],
                "agency_id": mapping[LinkAgencyMetaURL.agency_id],
            }
            potential_orphan_mappings.append(pom)
        if len(potential_orphan_mappings) > 0:
            raise OrphanedEntityException(
                f"Cannot delete agencies with meta URLs: {potential_orphan_mappings}"
            )

    def check_for_no_data_source_orphans(self) -> None:
        """
        Check that no data sources would be orphaned by this process
        If they would, raise error
        """

        removal_ids: list[int] = self.request.ids

        orphans_q = (
            select(LinkAgencyDataSource.data_source_id)
            .group_by(LinkAgencyDataSource.data_source_id)
            .having(  # nothing remains after removing these agencies
                func.count().filter(LinkAgencyDataSource.agency_id.notin_(removal_ids))
                == 0
            )
            .having(  # there was at least one link that would be removed
                func.count().filter(LinkAgencyDataSource.agency_id.in_(removal_ids)) > 0
            )
            .cte("orphans")
        )
        query = (
            select(LinkAgencyDataSource.agency_id, LinkAgencyDataSource.data_source_id)
            .join(
                orphans_q,
                LinkAgencyDataSource.data_source_id == orphans_q.c.data_source_id,
            )
            .where(LinkAgencyDataSource.agency_id.in_(removal_ids))
        )
        mappings: Sequence[RowMapping] = self.mappings(query)
        potential_orphan_mappings: list[dict[str, int]] = []
        for mapping in mappings:
            pom = {
                "data_source_id": mapping[LinkAgencyDataSource.data_source_id],
                "agency_id": mapping[LinkAgencyDataSource.agency_id],
            }
            potential_orphan_mappings.append(pom)
        if len(potential_orphan_mappings) > 0:
            raise OrphanedEntityException(
                f"Cannot delete agencies with data sources: {potential_orphan_mappings}"
            )
