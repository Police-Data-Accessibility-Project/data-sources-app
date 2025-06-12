from flask import make_response

from db.client import DatabaseClient
from middleware.flask_response_manager import FlaskResponseManager
from middleware.schema_and_dto.dtos.source_collector.duplicates import (
    SourceCollectorDuplicatesPostRequestDTO,
)
from middleware.schema_and_dto.dtos.source_collector.post.request import (
    SourceCollectorPostRequestDTO,
)
from middleware.util.url import normalize_url


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


def check_for_duplicate_urls(
    db_client: DatabaseClient, dto: SourceCollectorDuplicatesPostRequestDTO
):
    # First, normalize all urls
    d_normalized_urls_to_urls = {}
    for url in dto.urls:
        normalized_url = normalize_url(url)
        d_normalized_urls_to_urls[normalized_url] = url

    normalized_urls = list(d_normalized_urls_to_urls.keys())
    database_urls = db_client.get_duplicate_urls_bulk(normalized_urls)

    results = {}
    for normalized_url in normalized_urls:
        is_duplicate = normalized_url in database_urls
        results[d_normalized_urls_to_urls[normalized_url]] = is_duplicate

    return make_response({"results": results})
