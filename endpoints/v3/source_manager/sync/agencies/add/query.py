from db.models.implementations.links.agency__location import LinkAgencyLocation
from db.models.implementations.core.agency.core import Agency
from db.queries.builder.core import QueryBuilderBase
from endpoints.v3.source_manager.sync.agencies.add.request import AddAgenciesOuterRequest
from endpoints.v3.source_manager.sync.shared.models.response.add import (
    SourceManagerSyncAddOuterResponse,
    SourceManagerSyncAddInnerResponse,
)


class SourceManagerAddAgenciesQueryBuilder(QueryBuilderBase):
    def __init__(self, request: AddAgenciesOuterRequest):
        super().__init__()
        self.request = request

    def run(self) -> SourceManagerSyncAddOuterResponse:
        agency_inserts: list[Agency] = []
        for agency_request in self.request.agencies:
            agency_insert = Agency(
                name=agency_request.name,
                jurisdiction_type=agency_request.jurisdiction_type.value,
                agency_type=agency_request.agency_type.value,
                no_web_presence=agency_request.no_web_presence,
                defunct_year=agency_request.defunct_year,
            )
            agency_inserts.append(agency_insert)

        # Bulk Add and return IDs
        request_app_mappings: dict[int, int] = {}
        agency_ids: list[int] = self.add_many(
            agency_inserts,
            return_ids=True,
        )

        # Reconcile App IDs with request ids
        for agency_id, agency_request in zip(agency_ids, self.request.agencies):
            request_app_mappings[agency_request.request_id] = agency_id

        # Add Location Links
        link_inserts: list[LinkAgencyLocation] = []
        for agency_request in self.request.agencies:
            agency_id: int = request_app_mappings[agency_request.request_id]
            for location_id in agency_request.location_ids:
                link_insert = LinkAgencyLocation(
                    agency_id=agency_id, location_id=location_id
                )
                link_inserts.append(link_insert)

        self.add_many(link_inserts)

        inner_responses: list[SourceManagerSyncAddInnerResponse] = []
        for request_id, agency_id in request_app_mappings.items():
            inner_responses.append(
                SourceManagerSyncAddInnerResponse(
                    request_id=request_id,
                    app_id=agency_id,
                )
            )

        return SourceManagerSyncAddOuterResponse(
            entities=inner_responses,
        )
