from typing import Sequence

from sqlalchemy import select, RowMapping

from db.helpers_.url_mappings.mapper import URLMapper
from db.helpers_.url_mappings.model import URLMapping
from db.models.implementations.links.agency__data_source import LinkAgencyDataSource
from db.models.implementations.core.data_source.core import DataSource
from db.models.implementations.core.record.type import RecordType
from db.queries.builder.core import QueryBuilderBase
from endpoints.v3.source_manager.sync.data_sources.add.helpers import (
    _consolidate_responses,
    _value_if_not_none,
)
from endpoints.v3.source_manager.sync.data_sources.add.request import (
    AddDataSourcesOuterRequest,
)
from endpoints.v3.source_manager.sync.shared.add_mappings import AddMappings
from endpoints.v3.source_manager.sync.shared.models.response.add import (
    SourceManagerSyncAddOuterResponse,
)
from middleware.enums import RecordTypesEnum


class SourceManagerAddDataSourcesQueryBuilder(QueryBuilderBase):
    def __init__(self, request: AddDataSourcesOuterRequest):
        super().__init__()
        self.request = request

    def run(self) -> SourceManagerSyncAddOuterResponse:
        add_mappings: AddMappings = self._add_data_sources()

        # Add agency links
        self._add_agency_links(add_mappings)

        # Consolidate response
        inner_responses = _consolidate_responses(add_mappings.request_app_mappings)

        return SourceManagerSyncAddOuterResponse(
            entities=inner_responses,
        )

    def _get_preexisting_url_mappings(self, urls: list[str]) -> URLMapper:
        query = select(
            DataSource.source_url,
            DataSource.id,
        ).where(DataSource.source_url.in_(urls))
        mappings: Sequence[RowMapping] = self.mappings(query)
        return URLMapper(
            mappings=[
                URLMapping(
                    url=mapping[DataSource.source_url],
                    url_id=mapping[DataSource.id],
                )
                for mapping in mappings
            ]
        )

    def _add_data_sources(self) -> AddMappings:
        # Check whether any URLs are already in database
        urls: list[str] = [
            ds_request.content.source_url for ds_request in self.request.data_sources
        ]
        preexisting_url_mapper: URLMapper = self._get_preexisting_url_mappings(urls)

        record_type_id_mapping: dict[RecordTypesEnum, int] = (
            self.get_record_type_id_mapping()
        )
        data_source_inserts: list[DataSource] = []
        request_app_mappings: dict[int, int] = {}
        for ds_request in self.request.data_sources:
            content = ds_request.content
            # For preexisting URLs, just add to mappings and skip insert
            if preexisting_url_mapper.url_exists(content.source_url):
                url_id: int = preexisting_url_mapper.get_id(content.source_url)
                request_app_mappings[ds_request.request_id] = url_id
                continue

            ds_insert = DataSource(
                source_url=content.source_url,
                name=content.name,
                description=content.description,
                record_type_id=record_type_id_mapping[content.record_type],
                agency_supplied=content.agency_supplied,
                supplying_entity=content.supplying_entity,
                agency_originated=content.agency_originated,
                agency_aggregation=_value_if_not_none(content.agency_aggregation),
                coverage_start=content.coverage_start,
                coverage_end=content.coverage_end,
                detail_level=content.detail_level,
                access_types=[at.value for at in content.access_types]
                if content.access_types
                else None,
                data_portal_type=content.data_portal_type,
                record_formats=content.record_formats,
                update_method=_value_if_not_none(content.update_method),
                readme_url=content.readme_url,
                originating_entity=content.originating_entity,
                retention_schedule=_value_if_not_none(content.retention_schedule),
                scraper_url=content.scraper_url,
                agency_described_not_in_database=content.agency_described_not_in_database,
                data_portal_type_other=content.data_portal_type_other,
                access_notes=content.access_notes,
                url_status=_value_if_not_none(content.url_status),
                internet_archive_url=content.internet_archive_url,
            )
            data_source_inserts.append(ds_insert)
        # Add and get DS IDs
        ds_ids: list[int] = self.add_many(data_source_inserts, return_ids=True)
        for ds_id, ds_request in zip(ds_ids, self.request.data_sources):
            request_app_mappings[ds_request.request_id] = ds_id
        return AddMappings(
            request_app_mappings=request_app_mappings,
            preexisting_url_mapper=preexisting_url_mapper,
        )

    def _add_agency_links(self, add_mappings: AddMappings) -> None:
        link_inserts: list[LinkAgencyDataSource] = []
        request_app_mappings: dict[int, int] = add_mappings.request_app_mappings
        preexisting_mapper: URLMapper = add_mappings.preexisting_url_mapper
        for ds_request in self.request.data_sources:
            ds_id: int = request_app_mappings[ds_request.request_id]

            # For preexisting URLs, skip insert
            if preexisting_mapper.id_exists(ds_id):
                continue

            for agency_id in ds_request.content.agency_ids:
                link_insert = LinkAgencyDataSource(
                    data_source_id=ds_id, agency_id=agency_id
                )
                link_inserts.append(link_insert)
        self.add_many(link_inserts)

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
