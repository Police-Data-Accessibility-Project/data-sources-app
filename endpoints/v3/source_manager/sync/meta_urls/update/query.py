from typing import Any

from sqlalchemy import delete

from db.models.implementations import LinkAgencyMetaURL
from db.models.implementations.core.agency.meta_urls.sqlalchemy import MetaURL
from db.queries.builder.core import QueryBuilderBase
from endpoints.v3.source_manager.sync.meta_urls.update.request import (
    UpdateMetaURLsOuterRequest,
)
from utilities.common import value_if_enum


class SourceManagerUpdateMetaURLsQueryBuilder(QueryBuilderBase):
    def __init__(self, request: UpdateMetaURLsOuterRequest):
        super().__init__()
        self.request = request

    def run(self) -> None:
        bulk_update_mappings: list[dict[str, Any]] = []

        for meta_url_request in self.request.meta_urls:
            bum = {"id": meta_url_request.app_id}
            for key, value in meta_url_request.content.model_dump(
                exclude_unset=True
            ).items():
                if key in ("app_id",):
                    continue
                bum[key] = value_if_enum(value)
            # Skip if no updates
            if len(bum) == 1:
                continue
            bulk_update_mappings.append(bum)

        self.bulk_update_mappings(
            MetaURL,
            bulk_update_mappings,
        )

        # If any agency ids were provided, update the agency links
        mu_id_agency_id_mappings: dict[int, list[int]] = {}
        for meta_url_request in self.request.meta_urls:
            if meta_url_request.content.agency_ids is not None:
                mu_id_agency_id_mappings[meta_url_request.app_id] = (
                    meta_url_request.content.agency_ids
                )

        # Delete existing agency links
        statement = delete(LinkAgencyMetaURL).where(
            LinkAgencyMetaURL.meta_url_id.in_(mu_id_agency_id_mappings.keys())
        )
        self.execute(statement)

        # Add new agency links
        link_inserts: list[LinkAgencyMetaURL] = []
        for mu_id, agency_ids in mu_id_agency_id_mappings.items():
            for agency_id in agency_ids:
                link_insert = LinkAgencyMetaURL(meta_url_id=mu_id, agency_id=agency_id)
                link_inserts.append(link_insert)
        self.add_many(link_inserts)
