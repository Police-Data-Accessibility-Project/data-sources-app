from typing import Sequence

from sqlalchemy import select, RowMapping

from db.helpers_.url_mappings.mapper import URLMapper
from db.helpers_.url_mappings.model import URLMapping
from db.models.implementations import LinkAgencyMetaURL
from db.models.implementations.core.agency.meta_urls.sqlalchemy import MetaURL
from db.queries.builder.core import QueryBuilderBase
from endpoints.v3.source_manager.sync.meta_urls.add.request import (
    AddMetaURLsOuterRequest,
)
from endpoints.v3.source_manager.sync.shared.add_mappings import AddMappings
from endpoints.v3.source_manager.sync.shared.models.response.add import (
    SourceManagerSyncAddOuterResponse,
    SourceManagerSyncAddInnerResponse,
)


class SourceManagerAddMetaURLsQueryBuilder(QueryBuilderBase):
    def __init__(self, request: AddMetaURLsOuterRequest):
        super().__init__()
        self.request = request

    def run(self) -> SourceManagerSyncAddOuterResponse:
        # Add Meta URLs
        add_mappings: AddMappings = self._add_meta_urls()

        # Add Agency Links
        self._add_agency_links(add_mappings)

        # Reconcile App IDs with Request IDs
        inner_responses: list[SourceManagerSyncAddInnerResponse] = []
        for request_id, mu_id in add_mappings.request_app_mappings.items():
            inner_responses.append(
                SourceManagerSyncAddInnerResponse(
                    request_id=request_id,
                    app_id=mu_id,
                )
            )

        return SourceManagerSyncAddOuterResponse(
            entities=inner_responses,
        )

    def _add_agency_links(self, add_mappings: AddMappings) -> None:
        link_inserts: list[LinkAgencyMetaURL] = []
        request_app_mappings: dict[int, int] = add_mappings.request_app_mappings
        preexisting_mapper: URLMapper = add_mappings.preexisting_url_mapper
        for meta_url_request in self.request.meta_urls:
            mu_id: int = request_app_mappings[meta_url_request.request_id]

            # For preexisting URLs, skip insert
            if preexisting_mapper.id_exists(mu_id):
                continue

            for agency_id in meta_url_request.content.agency_ids:
                link_insert = LinkAgencyMetaURL(agency_id=agency_id, meta_url_id=mu_id)
                link_inserts.append(link_insert)
        self.add_many(link_inserts)

    def _get_preexisting_url_mappings(self, urls: list[str]) -> URLMapper:
        query = (
            select(
                MetaURL.url,
                MetaURL.id,
            )
            .where(
                MetaURL.url.in_(urls)
            )
        )
        mappings: Sequence[RowMapping] = self.mappings(query)
        return URLMapper(
            mappings=[
                URLMapping(
                    url=mapping[MetaURL.url],
                    url_id=mapping[MetaURL.id],
                )
                for mapping in mappings
            ]
        )

    def _add_meta_urls(self) -> AddMappings:
        meta_url_inserts: list[MetaURL] = []

        urls: list[str] = [
            meta_url_request.content.url
            for meta_url_request in self.request.meta_urls
        ]

        preexisting_url_mapper: URLMapper = self._get_preexisting_url_mappings(urls)
        request_app_mappings: dict[int, int] = {}

        for meta_url_request in self.request.meta_urls:
            # For preexisting URLs, just add to mappings and skip insert
            if preexisting_url_mapper.url_exists(meta_url_request.content.url):
                url_id: int = preexisting_url_mapper.get_id(meta_url_request.content.url)
                request_app_mappings[meta_url_request.request_id] = url_id
                continue

            content = meta_url_request.content
            meta_url_insert = MetaURL(
                url=content.url,
            )
            meta_url_inserts.append(meta_url_insert)

        # Add and get Meta URL IDs
        mu_ids: list[int] = self.add_many(meta_url_inserts, return_ids=True)
        for mu_id, meta_url_request in zip(mu_ids, self.request.meta_urls):
            request_app_mappings[meta_url_request.request_id] = mu_id
        return AddMappings(
            request_app_mappings=request_app_mappings,
            preexisting_url_mapper=preexisting_url_mapper,
        )
