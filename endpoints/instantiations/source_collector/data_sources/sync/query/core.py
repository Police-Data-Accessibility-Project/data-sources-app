# pyright: reportUnknownMemberType=false
from typing import final, override

from sqlalchemy import select, func, CTE, Select

from db.models.implementations import LinkAgencyDataSource
from db.models.implementations.core.data_source.core import DataSource
from db.models.implementations.core.record.type import RecordType
from db.queries.builder.core import QueryBuilderBase
from endpoints.instantiations.source_collector.data_sources.sync.dtos.request import (
    SourceCollectorSyncDataSourcesRequestDTO,
)
from endpoints.instantiations.source_collector.data_sources.sync.dtos.response import (
    SourceCollectorSyncDataSourcesResponseDTO,
    SourceCollectorSyncDataSourcesResponseInnerDTO,
)
from endpoints.instantiations.source_collector.data_sources.sync.query.ctes.agency_id import (
    AgencyIdsCTE,
)
from middleware.enums import RecordTypes


@final
class SourceCollectorSyncDataSourcesQueryBuilder(QueryBuilderBase):
    def __init__(self, dto: SourceCollectorSyncDataSourcesRequestDTO):
        super().__init__()
        self.updated_at = dto.updated_at
        self.page = dto.page

    def agency_ids_cte(self) -> CTE:
        return select(
            func.unnest(LinkAgencyDataSource.agency_id),
            LinkAgencyDataSource.data_source_id,
        ).cte(name="agency_ids")

    @override
    def run(self) -> SourceCollectorSyncDataSourcesResponseDTO:
        aic = AgencyIdsCTE()

        query: Select = (
            select(
                DataSource.id,
                DataSource.source_url,
                DataSource.name,
                DataSource.description,
                DataSource.approval_status,
                DataSource.url_status,
                DataSource.updated_at,
                RecordType.name.label("record_type_name"),
                aic.agency_ids,
            )
            .join(RecordType, DataSource.record_type_id == RecordType.id)
            .join(aic.query, DataSource.id == aic.data_source_id)
        )

        if self.updated_at is not None:
            query = query.where(DataSource.updated_at >= self.updated_at)

        query = (
            query.order_by(DataSource.updated_at.asc(), DataSource.id.asc())
            .offset((self.page - 1) * 1000)
            .limit(1000)
        )

        mappings = self.session.execute(query).mappings().all()
        results: list[SourceCollectorSyncDataSourcesResponseInnerDTO] = []
        for mapping in mappings:
            results.append(
                SourceCollectorSyncDataSourcesResponseInnerDTO(
                    id=mapping["id"],
                    url=mapping["source_url"],
                    name=mapping["name"],
                    description=mapping["description"],
                    approval_status=mapping["approval_status"],
                    url_status=mapping["url_status"],
                    updated_at=mapping["updated_at"],
                    record_type=RecordTypes(mapping["record_type_name"]),
                    agency_ids=mapping["agency_ids"],
                )
            )
        return SourceCollectorSyncDataSourcesResponseDTO(data_sources=results)
