from flask import make_response

from db.client.core import DatabaseClient
from endpoints.instantiations.source_collector.data_sources.post.dtos.request import (
    SourceCollectorPostRequestDTO,
)


def add_data_sources_from_source_collector(
    db_client: DatabaseClient, dto: SourceCollectorPostRequestDTO
):
    results = db_client.add_data_sources_from_source_collector(dto.data_sources)

    return make_response(
        {
            "message": "Successfully processed data sources",
            "data_sources": [result.model_dump(mode="json") for result in results],
        }
    )
