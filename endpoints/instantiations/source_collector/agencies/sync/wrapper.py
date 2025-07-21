from db.client.core import DatabaseClient
from endpoints.instantiations.source_collector.agencies.sync.dtos.request import (
    SourceCollectorSyncAgenciesRequestDTO,
)


def get_agencies_for_sync(
    db_client: DatabaseClient, dto: SourceCollectorSyncAgenciesRequestDTO
) -> dict[str, list[dict]]:
    return db_client.get_agencies_for_sync(dto=dto)
