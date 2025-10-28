from typing import Any

from db.models.implementations.core.agency.meta_urls.sqlalchemy import AgencyMetaURL
from db.queries.builder.core import QueryBuilderBase
from endpoints.v3.sync.meta_urls.update.request import UpdateMetaURLsOuterRequest


class SourceManagerUpdateMetaURLsQueryBuilder(QueryBuilderBase):
    def __init__(self, request: UpdateMetaURLsOuterRequest):
        super().__init__()
        self.request = request

    def run(self) -> None:
        bulk_update_mappings: list[dict[str, Any]] = []

        for meta_url_request in self.request.meta_urls:
            bum = {"id": meta_url_request.app_id}
            for key, value in meta_url_request.model_dump(exclude_unset=True).items():
                if key in ("app_id"):
                    continue
                bum[key] = value
            # Skip if no updates
            if len(bum) == 1:
                continue
            bulk_update_mappings.append(bum)

        self.bulk_update_mappings(
            AgencyMetaURL,
            bulk_update_mappings,
        )
