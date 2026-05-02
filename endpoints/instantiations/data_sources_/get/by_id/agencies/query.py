from sqlalchemy import select
from sqlalchemy.orm import selectinload

from db.models.implementations.core.agency.core import Agency
from db.models.implementations.core.data_source.core import DataSource
from db.queries.builder.core import QueryBuilderBase
from endpoints.instantiations.data_sources_.get.by_id.agencies.format import (
    agency_to_data_sources_get_related_agencies_output,
)


class GetDataSourceRelatedAgenciesQueryBuilder(QueryBuilderBase):
    def __init__(self, data_source_id: int) -> None:
        super().__init__()
        self.data_source_id = data_source_id

    def run(self) -> list[dict] | None:
        query = (
            select(DataSource)
            .options(
                selectinload(DataSource.agencies).selectinload(
                    Agency.locations
                ),
                selectinload(DataSource.agencies).selectinload(
                    Agency.meta_urls
                ),
            )
            .where(DataSource.id == self.data_source_id)
        )

        result: DataSource = (
            self.session.execute(query).scalars(DataSource).first()
        )
        if result is None:
            return None

        agency_dicts = []
        for agency in result.agencies:
            agency_dict = agency_to_data_sources_get_related_agencies_output(agency)
            agency_dicts.append(agency_dict)

        return agency_dicts
