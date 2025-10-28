from endpoints.v3.sync.agencies.update.query import (
    SourceManagerUpdateAgenciesQueryBuilder,
)
from endpoints.v3.sync.agencies.update.request import UpdateAgenciesOuterRequest
from endpoints.v3.sync.shared.functions import run_sync_query_builder
from middleware.schema_and_dto.dtos.common_dtos import MessageDTO


def source_manager_update_agencies(
    request: UpdateAgenciesOuterRequest,
) -> MessageDTO:
    return run_sync_query_builder(
        query_builder=SourceManagerUpdateAgenciesQueryBuilder(request)
    )
