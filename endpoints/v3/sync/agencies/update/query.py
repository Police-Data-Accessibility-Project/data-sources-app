from typing import Any

from sqlalchemy import delete

from db.models.implementations import LinkAgencyLocation
from db.models.implementations.core.agency.core import Agency
from db.queries.builder.core import QueryBuilderBase
from endpoints.v3.sync.agencies.update.request import UpdateAgenciesOuterRequest
from utilities.common import value_if_enum


class SourceManagerUpdateAgenciesQueryBuilder(QueryBuilderBase):
    def __init__(self, request: UpdateAgenciesOuterRequest):
        super().__init__()
        self.request = request

    def run(self) -> None:
        bulk_update_mappings: list[dict[str, Any]] = []

        for agency_request in self.request.agencies:
            bum = {"id": agency_request.app_id}
            for key, value in agency_request.model_dump(exclude_unset=True).items():
                if key in ("app_id", "location_ids"):
                    continue
                bum[key] = value_if_enum(value)
            # Skip if no updates
            if len(bum) == 1:
                continue
            bulk_update_mappings.append(bum)

        self.bulk_update_mappings(
            Agency,
            bulk_update_mappings,
        )

        # If any location_ids were provided, update the location links
        agency_id_location_id_mappings: dict[int, list[int]] = {}
        for agency_request in self.request.agencies:
            if agency_request.location_ids is not None:  # TODO: Mod.
                agency_id_location_id_mappings[agency_request.app_id] = (
                    agency_request.location_ids
                )

        # Delete existing location links
        statement = delete(LinkAgencyLocation).where(
            LinkAgencyLocation.agency_id.in_(agency_id_location_id_mappings.keys())
        )
        self.execute(statement)

        # Add new location links
        link_inserts: list[LinkAgencyLocation] = []
        for agency_id, location_ids in agency_id_location_id_mappings.items():
            for location_id in location_ids:
                link_insert = LinkAgencyLocation(
                    agency_id=agency_id, location_id=location_id
                )
                link_inserts.append(link_insert)
        self.add_many(link_inserts)
