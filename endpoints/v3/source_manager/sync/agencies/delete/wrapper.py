from db.client.core import DatabaseClient
from endpoints.v3.source_manager.sync.agencies.delete.query import (
    SourceManagerDeleteAgenciesQueryBuilder,
)
from endpoints.v3.source_manager.sync.shared.models.request.delete import SourceManagerDeleteRequest
from middleware.schema_and_dto.dtos.common_dtos import MessageDTO


def source_manager_delete_agencies(
    request: SourceManagerDeleteRequest,
) -> MessageDTO:
    db_client = DatabaseClient()
    db_client.run_query_builder(SourceManagerDeleteAgenciesQueryBuilder(request))
    return MessageDTO(message="Sync completed successfully")
