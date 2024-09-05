from dataclasses import dataclass
from http import HTTPStatus

from flask import Response, make_response

from database_client.database_client import DatabaseClient
from middleware.common_response_formatting import format_list_response, message_response


def get_agencies_without_homepage_urls(database_client: DatabaseClient) -> Response:
    results = database_client.get_agencies_without_homepage_urls()
    return make_response(format_list_response(results), 200)

@dataclass
class SearchCacheEntry:
    agency_airtable_uid: str
    search_results: list[str]

def update_search_cache(
    db_client: DatabaseClient, dto: SearchCacheEntry
) -> Response:

    for result in dto.search_results:
        db_client.create_search_cache_entry(
            column_value_mappings={
                "agency_airtable_uid": dto.agency_airtable_uid,
                "search_result": result
            }
        )
    return message_response("Search Cache Updated", HTTPStatus.OK)

