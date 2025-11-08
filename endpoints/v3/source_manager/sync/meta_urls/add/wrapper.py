from fastapi import HTTPException

from db.client.core import DatabaseClient
from endpoints.v3.source_manager.sync.meta_urls.add.query import (
    SourceManagerAddMetaURLsQueryBuilder,
)
from endpoints.v3.source_manager.sync.meta_urls.add.request import (
    AddMetaURLsOuterRequest,
)
from endpoints.v3.source_manager.sync.shared.models.response.add import (
    SourceManagerSyncAddOuterResponse,
)


def source_manager_add_meta_urls(
    request: AddMetaURLsOuterRequest,
) -> SourceManagerSyncAddOuterResponse:
    try:
        db_client = DatabaseClient()
        return db_client.run_query_builder(
            SourceManagerAddMetaURLsQueryBuilder(request)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
