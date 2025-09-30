from flask import make_response

from db.client.core import DatabaseClient
from endpoints.instantiations.source_collector.meta_urls.post.dtos.request import SourceCollectorMetaURLPostRequestDTO
from endpoints.instantiations.source_collector.meta_urls.post.dtos.response import SourceCollectorMetaURLPostResponseDTO
from endpoints.instantiations.source_collector.meta_urls.post.queries.core import \
    AddMetaURLsFromSourceCollectorQueryBuilder


def add_meta_urls_from_source_collector(
    db_client: DatabaseClient,
    dto: SourceCollectorMetaURLPostRequestDTO
):
    results: SourceCollectorMetaURLPostResponseDTO = db_client.run_query_builder(
        AddMetaURLsFromSourceCollectorQueryBuilder(dto.meta_urls)
    )

    return make_response(
        results.model_dump(mode="json")
    )