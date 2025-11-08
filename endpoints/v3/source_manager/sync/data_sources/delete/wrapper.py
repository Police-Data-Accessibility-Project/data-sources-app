from endpoints.v3.source_manager.sync.data_sources.delete.query import (
    SourceManagerDeleteDataSourcesQueryBuilder,
)
from endpoints.v3.source_manager.sync.shared.functions import run_sync_query_builder
from endpoints.v3.source_manager.sync.shared.models.request.delete import (
    SourceManagerDeleteRequest,
)
from middleware.schema_and_dto.dtos.common_dtos import MessageDTO


def source_manager_delete_data_sources(
    request: SourceManagerDeleteRequest,
) -> MessageDTO:
    return run_sync_query_builder(
        query_builder=SourceManagerDeleteDataSourcesQueryBuilder(request)
    )
