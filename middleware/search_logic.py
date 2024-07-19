from http import HTTPStatus
from typing import Optional

from flask import Response, make_response

from database_client.database_client import DatabaseClient
from database_client.result_formatter import ResultFormatter, dictify_namedtuple
from utilities.enums import RecordCategories


def search_wrapper(
    db_client: DatabaseClient,
    state: str,
    record_category: Optional[RecordCategories] = None,
    county: Optional[str] = None,
    locality: Optional[str] = None,
) -> Response:
    search_results = db_client.search_with_location_and_record_type(
        state=state, record_type=record_category, county=county, locality=locality
    )

    dict_results = dictify_namedtuple(search_results)
    # TODO: This is shared by other search routes such as quick-search. Consolidate i
    body = {
        "count": len(dict_results),
        "data": dict_results
    }
    return make_response(body, HTTPStatus.OK)
