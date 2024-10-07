from dataclasses import dataclass
from http import HTTPStatus
from typing import Optional

from flask import Response, make_response
from marshmallow import fields, Schema

from database_client.database_client import DatabaseClient
from database_client.result_formatter import dictify_namedtuple
from middleware.enums import JurisdictionSimplified
from utilities.common import get_enums_from_string
from utilities.enums import RecordCategories, SourceMappingEnum, ParserLocation
from middleware.common_response_formatting import format_list_response


def transform_record_categories(value: str) -> Optional[list[RecordCategories]]:
    if value is not None:
        return get_enums_from_string(RecordCategories, value, case_insensitive=True)
    return None


class SearchRequestSchema(Schema):
    state = fields.Str(
        required=True,
        metadata={
            "description": "The state of the search.",
            "source": SourceMappingEnum.QUERY_ARGS,
            "location": ParserLocation.QUERY.value,
        },
    )
    record_categories = fields.Str(
        required=False,
        metadata={
            "transformation_function": transform_record_categories,
            "description": "The record categories of the search. If empty, all categories will be searched."
            "Multiple record categories can be provided as a comma-separated list, eg. 'Police & Public "
            "Interactions,Agency-published Resources'."
            "Allowable record categories include: \n  * "
            + "\n  * ".join([e.value for e in RecordCategories]),
            "source": SourceMappingEnum.QUERY_ARGS,
            "location": ParserLocation.QUERY.value,
        },
    )
    county = fields.Str(
        required=False,
        metadata={
            "description": "The county of the search. If empty, all counties for the given state will be searched.",
            "source": SourceMappingEnum.QUERY_ARGS,
            "location": ParserLocation.QUERY.value,
        },
    )
    locality = fields.Str(
        required=False,
        metadata={
            "description": "The locality of the search. If empty, all localities for the given county will be searched.",
            "source": SourceMappingEnum.QUERY_ARGS,
            "location": ParserLocation.QUERY.value,
        },
    )


@dataclass
class SearchRequests:
    state: str
    record_categories: Optional[list[RecordCategories]] = None
    county: Optional[str] = None
    locality: Optional[str] = None


def get_jursidiction_type_enum(
    jurisdiction_type_str: str,
) -> Optional[JurisdictionSimplified]:
    if jurisdiction_type_str in [
        "local",
        "school",
        "military",
        "tribal",
        "transit",
        "port",
    ]:
        return JurisdictionSimplified.LOCALITY
    return JurisdictionSimplified(jurisdiction_type_str)


def format_search_results(search_results: list[dict]) -> dict:
    """
    Convert results to the following format:

    {
      "count": <number>,
      "data": {
          "federal": {
            "count": <number>,
            "results": [<data-source-record>]
          }
          "state": {
            "count": <number>,
            "results": [<data-source-record>]
          },
          county: {
            "count": <number>,
            "results": [<data-source-record>]
          },
          locality: {
            "count": <number>,
            "results": [<data-source-record>]
          },
        }
    }

    :param search_results:
    :return:
    """

    response = {"count": 0, "data": {}}

    # Create sub-dictionary for each jurisdiction
    for jurisdiction in [j.value for j in JurisdictionSimplified]:
        response["data"][jurisdiction] = {"count": 0, "results": []}

    for result in search_results:
        jurisdiction_str = result.get("jurisdiction_type")
        jurisdiction = get_jursidiction_type_enum(jurisdiction_str)
        response["data"][jurisdiction.value]["count"] += 1
        response["data"][jurisdiction.value]["results"].append(result)
        response["count"] += 1

    return response


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
    formatted_search_results = format_search_results(search_results)
    return make_response(formatted_search_results, HTTPStatus.OK)
