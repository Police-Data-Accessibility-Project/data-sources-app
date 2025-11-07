from enum import Enum
from typing import Sequence

from sqlalchemy import select, RowMapping

from db.models.implementations.links.agency__data_source import LinkAgencyDataSource
from db.models.implementations.core.data_source.core import DataSource
from db.models.implementations.core.record.type import RecordType
from db.queries.builder.core import QueryBuilderBase
from endpoints.v3.source_manager.sync.data_sources.add.request import AddDataSourcesOuterRequest
from endpoints.v3.source_manager.sync.shared.models.response.add import (
    SourceManagerSyncAddOuterResponse,
    SourceManagerSyncAddInnerResponse,
)
from middleware.enums import RecordTypesEnum


def _value_if_not_none(value: Enum | None) -> str | None:
    if value is None:
        return None
    return value.value


class SourceManagerAddDataSourcesQueryBuilder(QueryBuilderBase):
    def __init__(self, request: AddDataSourcesOuterRequest):
        super().__init__()
        self.request = request

    def run(self) -> SourceManagerSyncAddOuterResponse:
        record_type_id_mapping: dict[RecordTypesEnum, int] = (
            self.get_record_type_id_mapping()
        )

        data_source_inserts: list[DataSource] = []
        for ds_request in self.request.data_sources:
            ds_insert = DataSource(
                source_url=ds_request.url,
                name=ds_request.name,
                description=ds_request.description,
                record_type_id=record_type_id_mapping[ds_request.record_type],
                agency_supplied=ds_request.agency_supplied,
                supplying_entity=ds_request.supplying_entity,
                agency_originated=ds_request.agency_originated,
                agency_aggregation=_value_if_not_none(ds_request.agency_aggregation),
                coverage_start=ds_request.coverage_start,
                coverage_end=ds_request.coverage_end,
                detail_level=ds_request.detail_level,
                access_types=[at.value for at in ds_request.access_types]
                if ds_request.access_types
                else None,
                data_portal_type=ds_request.data_portal_type,
                record_formats=ds_request.record_formats,
                update_method=_value_if_not_none(ds_request.update_method),
                readme_url=ds_request.readme_url,
                originating_entity=ds_request.originating_entity,
                retention_schedule=_value_if_not_none(ds_request.retention_schedule),
                scraper_url=ds_request.scraper_url,
                agency_described_not_in_database=ds_request.agency_described_not_in_database,
                data_portal_type_other=ds_request.data_portal_type_other,
                access_notes=ds_request.access_notes,
                url_status=_value_if_not_none(ds_request.url_status),
            )
            data_source_inserts.append(ds_insert)

        # Add and get DS IDs
        request_app_mappings: dict[int, int] = {}
        ds_ids: list[int] = self.add_many(data_source_inserts, return_ids=True)
        for ds_id, ds_request in zip(ds_ids, self.request.data_sources):
            request_app_mappings[ds_request.request_id] = ds_id

        # Add agency links
        link_inserts: list[LinkAgencyDataSource] = []
        for ds_request in self.request.data_sources:
            ds_id: int = request_app_mappings[ds_request.request_id]
            for agency_id in ds_request.agency_ids:
                link_insert = LinkAgencyDataSource(
                    data_source_id=ds_id, agency_id=agency_id
                )
                link_inserts.append(link_insert)

        self.add_many(link_inserts)

        # Consolidate response
        inner_responses: list[SourceManagerSyncAddInnerResponse] = []
        for request_id, ds_id in request_app_mappings.items():
            inner_responses.append(
                SourceManagerSyncAddInnerResponse(
                    request_id=request_id,
                    app_id=ds_id,
                )
            )

        return SourceManagerSyncAddOuterResponse(
            entities=inner_responses,
        )

    def get_record_type_id_mapping(self) -> dict[RecordTypesEnum, int]:
        query = select(
            RecordType.id,
            RecordType.name,
        )
        mappings: Sequence[RowMapping] = self.mappings(query)
        return {
            RecordTypesEnum(mapping[RecordType.name]): mapping[RecordType.id]
            for mapping in mappings
        }
