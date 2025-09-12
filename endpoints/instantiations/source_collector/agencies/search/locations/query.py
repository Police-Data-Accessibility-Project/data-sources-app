from collections import defaultdict
from typing import Sequence

from sqlalchemy import values, column, Integer, String, select, func, RowMapping

from db.models.implementations import LinkAgencyLocation
from db.models.implementations.core.location.core import Location
from db.models.implementations.core.location.us_state import USState
from db.models.implementations.materialized_views.typeahead.locations import (
    TypeaheadLocations,
)
from db.queries.builder.core import QueryBuilderBase
from endpoints.instantiations.source_collector.agencies.search.locations.dtos.request import (
    SourceCollectorAgencySearchLocationRequestDTO,
)
from endpoints.instantiations.source_collector.agencies.search.locations.dtos.response import (
    SourceCollectorAgencySearchLocationResponseDTO,
    InnerSearchLocationResponse,
    SearchLocationRequestResponse,
)

from db.helpers_ import session as sh


class SourceCollectorAgencySearchLocationQueryBuilder(QueryBuilderBase):
    def __init__(self, dto: SourceCollectorAgencySearchLocationRequestDTO):
        super().__init__()
        self.dto = dto

    def run(self) -> SourceCollectorAgencySearchLocationResponseDTO:
        queries_as_tups: list[tuple[int, str, str]] = [
            (
                request.request_id,
                request.query,
                request.iso,
            )
            for request in self.dto.requests
        ]

        vals = (
            values(
                column("request_id", Integer),
                column("query", String),
                column("iso", String),
                name="input_queries",
            )
            .data(queries_as_tups)
            .alias("input_queries_alias")
        )

        locations_with_agencies = (
            select(
                Location.id.label("location_id"),
                USState.state_iso.label("iso"),
            )
            .join(
                LinkAgencyLocation,
                Location.id == LinkAgencyLocation.location_id,
            )
            .join(
                USState,
                Location.state_id == USState.id,
            )
            .group_by(Location.id, USState.state_iso)
            .having(
                func.count(LinkAgencyLocation.agency_id) >= 1,
            )
            .cte("locations_with_agencies")
        )

        similarity = func.similarity(
            vals.c.query,
            TypeaheadLocations.search_name,
        )

        lateral_top_5 = (
            select(
                vals.c.request_id,
                TypeaheadLocations.location_id,
                LinkAgencyLocation.agency_id,
                similarity.label("similarity"),
            )
            .join(
                LinkAgencyLocation,
                TypeaheadLocations.location_id == LinkAgencyLocation.location_id,
            )
            .join(
                locations_with_agencies,
                TypeaheadLocations.location_id == locations_with_agencies.c.location_id,
            )
            .where(
                locations_with_agencies.c.iso == vals.c.iso,
            )
            .order_by(
                similarity.desc(),
            )
            .limit(5)
            .lateral("lateral_top_5")
        )

        final = select(
            vals.c.request_id,
            lateral_top_5.c.agency_id,
            lateral_top_5.c.similarity,
        ).join(
            lateral_top_5,
            vals.c.request_id == lateral_top_5.c.request_id,
        )

        mappings: Sequence[RowMapping] = sh.mappings(self.session, query=final)
        request_id_to_inner_dtos: dict[int, list[InnerSearchLocationResponse]] = (
            defaultdict(list)
        )
        for mapping in mappings:
            inner_response = InnerSearchLocationResponse(
                agency_id=mapping["agency_id"],
                similarity=mapping["similarity"],
            )
            request_id: int = mapping["request_id"]
            request_id_to_inner_dtos[request_id].append(inner_response)

        responses: list[SearchLocationRequestResponse] = []

        for request_id, inner_dtos in request_id_to_inner_dtos.items():
            sorted_dtos: list[InnerSearchLocationResponse] = sorted(
                inner_dtos, key=lambda dto: dto.similarity, reverse=True
            )
            response = SearchLocationRequestResponse(
                request_id=request_id,
                results=sorted_dtos,
            )
            responses.append(response)

        return SourceCollectorAgencySearchLocationResponseDTO(
            responses=responses,
        )
