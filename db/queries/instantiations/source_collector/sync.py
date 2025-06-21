from typing import Any

from sqlalchemy import select

from db.enums import ApprovalStatus
from db.models.implementations import LinkAgencyLocation
from db.models.implementations.core.agency.core import Agency
from db.models.implementations.core.location.core import Location
from db.models.implementations.core.location.county import County
from db.models.implementations.core.location.locality import Locality
from db.models.implementations.core.location.us_state import USState
from db.queries.builder import QueryBuilderBase
from endpoints.instantiations.source_collector.sync.dtos.request import (
    SourceCollectorSyncAgenciesRequestDTO,
)
from middleware.constants import DATETIME_FORMAT


class SourceCollectorSyncAgenciesQueryBuilder(QueryBuilderBase):

    def __init__(self, dto: SourceCollectorSyncAgenciesRequestDTO):
        super().__init__()
        self.updated_at = dto.updated_at
        self.page = dto.page

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
            .join(
                LinkAgencyLocation,
                Agency.id == LinkAgencyLocation.agency_id,
            )
            .join(
                Location,
                LinkAgencyLocation.location_id == Location.id,
                isouter=True,
            )
            .join(
                USState,
                Location.state_id == USState.id,
                isouter=True,
            )
            .join(
                County,
                Location.county_id == County.id,
                isouter=True,
            )
            .join(
                Locality,
                Location.locality_id == Locality.id,
                isouter=True,
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

        return {"agencies": results}
