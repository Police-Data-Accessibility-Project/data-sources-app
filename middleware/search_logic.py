from dataclasses import dataclass
from http import HTTPStatus
from typing import Optional

from flask import Response, make_response

from database_client.database_client import DatabaseClient
from database_client.result_formatter import dictify_namedtuple
from utilities.common import get_enums_from_string
from utilities.enums import RecordCategories
from middleware.util import format_list_response


def transform_record_categories(value: str) -> Optional[list[RecordCategories]]:
    if value is not None:
        return get_enums_from_string(RecordCategories, value, case_insensitive=True)
    return None


@dataclass
class SearchRequests:
    state: str
    record_categories: Optional[list[RecordCategories]] = None
    county: Optional[str] = None
    locality: Optional[str] = None


def search_wrapper(
    db_client: DatabaseClient,
    dto: SearchRequests,
) -> Response:
    search_results = db_client.search_with_location_and_record_type(
        state=dto.state,
        record_categories=dto.record_categories,
        county=dto.county,
        locality=dto.locality,
    )

    dict_results = dictify_namedtuple(search_results)
    return make_response(format_list_response(dict_results), HTTPStatus.OK)
