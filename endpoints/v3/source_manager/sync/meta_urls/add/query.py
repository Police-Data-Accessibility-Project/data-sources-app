from db.models.implementations import LinkAgencyMetaURL
from db.models.implementations.core.agency.meta_urls.sqlalchemy import MetaURL
from db.queries.builder.core import QueryBuilderBase
from endpoints.v3.source_manager.sync.meta_urls.add.request import (
    AddMetaURLsOuterRequest,
)
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
        meta_url_inserts: list[MetaURL] = []
        for meta_url_request in self.request.meta_urls:
            content = meta_url_request.content
            meta_url_insert = MetaURL(
                url=content.url,
            )
            meta_url_inserts.append(meta_url_insert)

        # Add and get Meta URL IDs
        request_app_mappings: dict[int, int] = {}
        mu_ids: list[int] = self.add_many(meta_url_inserts, return_ids=True)
        for mu_id, meta_url_request in zip(mu_ids, self.request.meta_urls):
            request_app_mappings[meta_url_request.request_id] = mu_id

        # Add Agency Links
        link_inserts: list[LinkAgencyMetaURL] = []
        for meta_url_request in self.request.meta_urls:
            mu_id: int = request_app_mappings[meta_url_request.request_id]
            for agency_id in meta_url_request.content.agency_ids:
                link_insert = LinkAgencyMetaURL(agency_id=agency_id, meta_url_id=mu_id)
                link_inserts.append(link_insert)
        self.add_many(link_inserts)

        # Reconcile App IDs with Request IDs
        inner_responses: list[SourceManagerSyncAddInnerResponse] = []
        for request_id, mu_id in request_app_mappings.items():
            inner_responses.append(
                SourceManagerSyncAddInnerResponse(
                    request_id=request_id,
                    app_id=mu_id,
                )
            )

        return SourceManagerSyncAddOuterResponse(
            entities=inner_responses,
        )
