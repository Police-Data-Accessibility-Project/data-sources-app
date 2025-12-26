from db.client.core import DatabaseClient
from endpoints.v3.source_manager.data_sources.duplicate.request import SourceManagerDataSourcesDuplicateRequest
from endpoints.v3.source_manager.data_sources.duplicate.response import SourceManagerDataSourcesDuplicateResponse
from middleware.util.url import normalize_url


def check_for_duplicate_urls(
    db_client: DatabaseClient, request: SourceManagerDataSourcesDuplicateRequest
) -> SourceManagerDataSourcesDuplicateResponse:
    # First, normalize all urls
    d_normalized_urls_to_urls = {}
    for url in request.urls:
        normalized_url = normalize_url(url)
        d_normalized_urls_to_urls[normalized_url] = url

    normalized_urls = list(d_normalized_urls_to_urls.keys())
    database_urls = db_client.get_duplicate_urls_bulk(normalized_urls)

    results = {}
    for normalized_url in normalized_urls:
        is_duplicate = normalized_url in database_urls
        results[d_normalized_urls_to_urls[normalized_url]] = is_duplicate

    return SourceManagerDataSourcesDuplicateResponse(
        results=results,
    )