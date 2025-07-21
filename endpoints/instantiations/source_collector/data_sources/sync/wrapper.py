from flask import Response

from db.client.core import DatabaseClient
from endpoints.instantiations.source_collector.data_sources.sync.dtos.request import (
    SourceCollectorSyncDataSourcesRequestDTO,
)
from middleware.common_response_formatting import dto_to_response


def get_data_sources_for_sync(
    db_client: DatabaseClient, dto: SourceCollectorSyncDataSourcesRequestDTO
) -> Response:
    return dto_to_response(db_client.get_data_sources_for_sync(dto=dto))
