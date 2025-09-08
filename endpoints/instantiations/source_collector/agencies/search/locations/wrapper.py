from flask import Response

from db.client.core import DatabaseClient
from endpoints.instantiations.source_collector.agencies.search.locations.dtos.request import \
    SourceCollectorAgencySearchLocationRequestDTO
from endpoints.instantiations.source_collector.agencies.search.locations.dtos.response import \
    SourceCollectorAgencySearchLocationResponseDTO
from endpoints.instantiations.source_collector.agencies.search.locations.query import \
    SourceCollectorAgencySearchLocationQueryBuilder


def source_collector_search_agencies_by_location(
    db_client: DatabaseClient,
    dto: SourceCollectorAgencySearchLocationRequestDTO
) -> Response:
    qb = SourceCollectorAgencySearchLocationQueryBuilder(dto=dto)
    response: SourceCollectorAgencySearchLocationResponseDTO = \
        db_client.run_query_builder(qb)
    return response.model_dump(mode="json")
