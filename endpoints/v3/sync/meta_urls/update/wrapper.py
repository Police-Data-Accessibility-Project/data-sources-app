from endpoints.v3.sync.meta_urls.update.query import SourceManagerUpdateMetaURLsQueryBuilder
from endpoints.v3.sync.meta_urls.update.request import UpdateMetaURLsOuterRequest
from endpoints.v3.sync.shared.functions import run_sync_query_builder
from middleware.schema_and_dto.dtos.common_dtos import MessageDTO


def source_manager_update_meta_urls(
    request: UpdateMetaURLsOuterRequest,
) -> MessageDTO:
    return run_sync_query_builder(
        query_builder=SourceManagerUpdateMetaURLsQueryBuilder(request)
    )