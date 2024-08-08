from http import HTTPStatus
from typing import Optional

from flask import Response, make_response

from database_client.database_client import DatabaseClient
from database_client.result_formatter import ResultFormatter, dictify_namedtuple
from utilities.enums import RecordCategories
from middleware.util import format_list_response

def search_wrapper(
    db_client: DatabaseClient,
    state: str,
    record_categories: Optional[list[RecordCategories]] = None,
    county: Optional[str] = None,
    locality: Optional[str] = None,
) -> Response:
    search_results = db_client.search_with_location_and_record_type(
        state=state, record_categories=record_categories, county=county, locality=locality
    )

    dict_results = dictify_namedtuple(search_results)
    return make_response(format_list_response(dict_results), HTTPStatus.OK)
