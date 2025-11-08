from endpoints.v3.source_manager.sync.data_sources.update.query import (
    SourceManagerUpdateDataSourcesQueryBuilder,
)
from endpoints.v3.source_manager.sync.data_sources.update.request import (
    UpdateDataSourcesOuterRequest,
)
from endpoints.v3.source_manager.sync.shared.functions import run_sync_query_builder
from middleware.schema_and_dto.dtos.common_dtos import MessageDTO


def source_manager_update_data_sources(
    request: UpdateDataSourcesOuterRequest,
) -> MessageDTO:
    return run_sync_query_builder(
        query_builder=SourceManagerUpdateDataSourcesQueryBuilder(request)
    )
