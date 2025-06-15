from db.client.core import DatabaseClient
from endpoints.instantiations.source_collector.sync.dtos.request import (
    SourceCollectorSyncAgenciesRequestDTO,
)


def get_agencies_for_sync(
    db_client: DatabaseClient, dto: SourceCollectorSyncAgenciesRequestDTO
):
    return db_client.get_agencies_for_sync(dto=dto)
