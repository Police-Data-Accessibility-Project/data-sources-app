from typing import Any

from sqlalchemy import delete

from db.models.implementations.links.agency__data_source import LinkAgencyDataSource
from db.models.implementations.core.data_source.core import DataSource
from db.queries.builder.core import QueryBuilderBase
from endpoints.v3.source_manager.sync.data_sources.update.request import (
    UpdateDataSourcesOuterRequest,
)
from utilities.common import value_if_enum


class SourceManagerUpdateDataSourcesQueryBuilder(QueryBuilderBase):
    def __init__(self, request: UpdateDataSourcesOuterRequest):
        super().__init__()
        self.request = request

    def run(self) -> None:
        bulk_update_mappings: list[dict[str, Any]] = []

        for data_source_request in self.request.data_sources:
            bum = {"id": data_source_request.app_id}
            for key, value in data_source_request.model_dump(
                exclude_unset=True
            ).items():
                if key in ("app_id", "agency_ids"):
                    continue
                bum[key] = value_if_enum(value)
            # Skip if no updates
            if len(bum) == 1:
                continue
            bulk_update_mappings.append(bum)

        self.bulk_update_mappings(
            DataSource,
            bulk_update_mappings,
        )

        # If any agency ids were provided, update the agency links
        ds_id_agency_id_mappings: dict[int, list[int]] = {}
        for data_source_request in self.request.data_sources:
            if data_source_request.agency_ids is not None:
                ds_id_agency_id_mappings[data_source_request.app_id] = (
                    data_source_request.agency_ids
                )

        # Delete existing agency links
        statement = delete(LinkAgencyDataSource).where(
            LinkAgencyDataSource.data_source_id.in_(ds_id_agency_id_mappings.keys())
        )
        self.execute(statement)

        # Add new location links
        link_inserts: list[LinkAgencyDataSource] = []
        for ds_id, agency_ids in ds_id_agency_id_mappings.items():
            for agency_id in agency_ids:
                link_insert = LinkAgencyDataSource(
                    data_source_id=ds_id, agency_id=agency_id
                )
                link_inserts.append(link_insert)
        self.add_many(link_inserts)
