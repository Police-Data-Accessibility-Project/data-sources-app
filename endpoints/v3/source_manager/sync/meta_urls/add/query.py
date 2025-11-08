from db.models.implementations.core.agency.meta_urls.sqlalchemy import AgencyMetaURL
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
        meta_url_inserts: list[AgencyMetaURL] = []
        for meta_url_request in self.request.meta_urls:
            meta_url_insert = AgencyMetaURL(
                agency_id=meta_url_request.agency_id,
                url=meta_url_request.url,
            )
            meta_url_inserts.append(meta_url_insert)

        request_app_mappings: dict[int, int] = {}
        mu_ids: list[int] = self.add_many(meta_url_inserts, return_ids=True)
        for mu_id, meta_url_request in zip(mu_ids, self.request.meta_urls):
            request_app_mappings[meta_url_request.request_id] = mu_id

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
