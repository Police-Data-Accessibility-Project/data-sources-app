from fastapi import HTTPException

from db.client.core import DatabaseClient
from endpoints.v3.source_manager.sync.agencies.add.query import (
    SourceManagerAddAgenciesQueryBuilder,
)
from endpoints.v3.source_manager.sync.agencies.add.request import (
    AddAgenciesOuterRequest,
)
from endpoints.v3.source_manager.sync.shared.functions import run_sync_query_builder
from endpoints.v3.source_manager.sync.shared.models.response.add import (
    SourceManagerSyncAddOuterResponse,
)


def source_manager_add_agencies(
    request: AddAgenciesOuterRequest,
) -> SourceManagerSyncAddOuterResponse:
    return run_sync_query_builder(SourceManagerAddAgenciesQueryBuilder(request))
