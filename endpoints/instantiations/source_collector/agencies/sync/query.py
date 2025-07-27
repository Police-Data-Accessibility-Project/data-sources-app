from typing import Any, override, final

from sqlalchemy import select

from db.enums import ApprovalStatus
from db.models.implementations import LinkAgencyLocation
from db.models.implementations.core.agency.core import Agency
from db.models.implementations.core.location.core import Location
from db.models.implementations.core.location.county import County
from db.models.implementations.core.location.locality import Locality
from db.models.implementations.core.location.us_state import USState
from db.queries.builder.core import QueryBuilderBase
from endpoints.instantiations.source_collector.agencies.sync.dtos.request import (
    SourceCollectorSyncAgenciesRequestDTO,
)
from middleware.constants import DATETIME_FORMAT


@final
class SourceCollectorSyncAgenciesQueryBuilder(QueryBuilderBase):
    def __init__(self, dto: SourceCollectorSyncAgenciesRequestDTO):
        super().__init__()
        self.updated_at = dto.updated_at
        self.page = dto.page

    @override
    def run(self) -> Any:
        query = (
            select(
                Agency.id.label("agency_id"),
                Agency.name.label("display_name"),
                Location.type.label("location_type"),
                USState.state_name.label("state_name"),
                County.name.label("county_name"),
                Locality.name.label("locality_name"),
                Agency.updated_at,
            )
            .outerjoin(
                LinkAgencyLocation,
                Agency.id == LinkAgencyLocation.agency_id,
            )
            .outerjoin(
                Location,
                LinkAgencyLocation.location_id == Location.id,
            )
            .outerjoin(
                USState,
                Location.state_id == USState.id,
            )
            .outerjoin(
                County,
                Location.county_id == County.id,
            )
            .outerjoin(
                Locality,
                Location.locality_id == Locality.id,
            )
            .where(
                Agency.approval_status == ApprovalStatus.APPROVED.value,
            )
        )

        if self.updated_at is not None:
            query = query.where(Agency.updated_at >= self.updated_at)

        query = (
            query.order_by(Agency.updated_at.asc(), Agency.id.asc())
            .offset((self.page - 1) * 1000)
            .limit(1000)
        )

        mappings = self.session.execute(query).mappings().all()
        results = self._process_results(mappings)

        return {"agencies": results}

    def _process_results(self, mappings):
        results = []
        for mapping in mappings:
            results.append(
                {
                    "agency_id": mapping.agency_id,
                    "display_name": mapping.display_name,
                    "state_name": mapping.state_name,
                    "county_name": mapping.county_name,
                    "locality_name": mapping.locality_name,
                    "updated_at": mapping.updated_at.strftime(DATETIME_FORMAT),
                }
            )
        return results
