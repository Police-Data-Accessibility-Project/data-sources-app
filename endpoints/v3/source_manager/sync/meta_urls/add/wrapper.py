from endpoints.v3.source_manager.sync.meta_urls.add.query import (
    SourceManagerAddMetaURLsQueryBuilder,
)
from endpoints.v3.source_manager.sync.meta_urls.add.request import (
    AddMetaURLsOuterRequest,
)
from endpoints.v3.source_manager.sync.shared.functions import run_sync_query_builder
from endpoints.v3.source_manager.sync.shared.models.response.add import (
    SourceManagerSyncAddOuterResponse,
)


def source_manager_add_meta_urls(
    request: AddMetaURLsOuterRequest,
) -> SourceManagerSyncAddOuterResponse:
    return run_sync_query_builder(
        SourceManagerAddMetaURLsQueryBuilder(request)
    )