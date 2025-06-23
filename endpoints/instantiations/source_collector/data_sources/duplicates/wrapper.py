from flask import make_response

from db.client.core import DatabaseClient
from endpoints.instantiations.source_collector.data_sources.duplicates.dto import (
    SourceCollectorDuplicatesPostRequestDTO,
)
from middleware.util.url import normalize_url


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
