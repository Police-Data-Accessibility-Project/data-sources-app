from fastapi import HTTPException

from db.client.core import DatabaseClient
from endpoints.v3.source_manager.sync.data_sources.add.query import (
    SourceManagerAddDataSourcesQueryBuilder,
)
from endpoints.v3.source_manager.sync.data_sources.add.request import (
    AddDataSourcesOuterRequest,
)
from endpoints.v3.source_manager.sync.shared.functions import run_sync_query_builder
from endpoints.v3.source_manager.sync.shared.models.response.add import (
    SourceManagerSyncAddOuterResponse,
)


def source_manager_add_data_sources(
    request: AddDataSourcesOuterRequest,
) -> SourceManagerSyncAddOuterResponse:
    return run_sync_query_builder(
        SourceManagerAddDataSourcesQueryBuilder(request)
    )
