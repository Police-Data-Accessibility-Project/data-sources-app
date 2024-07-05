from collections import namedtuple

import spacy
import json
from http import HTTPStatus

from flask import make_response, Response

from database_client.database_client import DatabaseClient
from middleware.webhook_logic import post_to_webhook
from utilities.common import convert_dates_to_strings, format_arrays
from typing import List, Dict, Any

QUICK_SEARCH_COLUMNS = [
    "airtable_uid",
    "data_source_name",
    "description",
    "record_type",
    "source_url",
    "record_format",
    "coverage_start",
    "coverage_end",
    "agency_supplied",
    "agency_name",
    "municipality",
    "state_iso",
]


INSERT_LOG_QUERY = """
    INSERT INTO quick_search_query_logs 
    (search, location, results, result_count) 
    VALUES (%s, %s, %s, %s)
    """


def depluralize(term: str):
    """
    Depluralizes a given term using lemmatization.

    :param term: The term to be depluralized.
    :return: The depluralized term.
    """
    nlp = spacy.load("en_core_web_sm")
    term = term.strip()
    doc = nlp(term)
    lemmatized_tokens = [token.lemma_ for token in doc]
    depluralized_search_term = " ".join(lemmatized_tokens)
    return depluralized_search_term


SearchParameters = namedtuple("SearchParameters", ["search", "location"])


def quick_search_query(
    search_parameters: SearchParameters,
    db_client: DatabaseClient,
) -> Dict[str, Any]:
    """
    Performs a quick search using both unaltered and lemmatized search terms, returning the more fruitful result set.
    :param search_parameters:
    :param db_client: The database client.
    :return: A dictionary with the count of results and the data itself.
    """

    processed_search_parameters = process_search_parameters(search_parameters)

    data_source_matches = get_data_source_matches(db_client, processed_search_parameters)
    processed_data_source_matches = process_data_source_matches(data_source_matches)

    data_sources = {
        "count": len(processed_data_source_matches.converted),
        "data": processed_data_source_matches.converted,
    }
    db_client.add_quick_search_log(
        data_sources["count"],
        processed_data_source_matches,
        processed_search_parameters,
    )

    return data_sources


# DatabaseClient.add_quick_search_log()
def log_query(
    cursor,
    data_sources_count,
    processed_data_source_matches,
    processed_search_parameters,
):
    query_results = json.dumps(processed_data_source_matches.ids).replace("'", "")
    cursor.execute(
        INSERT_LOG_QUERY,
        (
            processed_search_parameters.search,
            processed_search_parameters.location,
            query_results,
            data_sources_count,
        ),
    )


def process_search_parameters(raw_sp: SearchParameters) -> SearchParameters:
    return SearchParameters(
        search="" if raw_sp.search == "all" else raw_sp.search.replace("'", ""),
        location="" if raw_sp.location == "all" else raw_sp.location.replace("'", ""),
    )


DataSourceMatches = namedtuple("DataSourceMatches", ["converted", "ids"])


def process_data_source_matches(data_source_matches: List[dict]) -> DataSourceMatches:
    data_source_matches_converted = []
    data_source_matches_ids = []
    for data_source_match in data_source_matches:
        data_source_match = convert_dates_to_strings(data_source_match)
        data_source_matches_converted.append(format_arrays(data_source_match))
        # Add ids to list for logging
        data_source_matches_ids.append(data_source_match["airtable_uid"])
    return DataSourceMatches(data_source_matches_converted, data_source_matches_ids)


def get_data_source_matches(
    db_client: DatabaseClient, sp: SearchParameters
) -> List[Dict[str, Any]]:

    unaltered_results = db_client.get_quick_search_results(sp.search, sp.location)

    spacy_results = db_client.get_quick_search_results(
        search=depluralize(sp.search), location=sp.location.strip())

    # Compare altered search term results with unaltered search term results, return the longer list
    results = (
        spacy_results
        if len(spacy_results) > len(unaltered_results)
        else unaltered_results
    )
    data_source_matches = [
        dict(zip(QUICK_SEARCH_COLUMNS, result)) for result in results
    ]
    return data_source_matches


def quick_search_query_wrapper(
    arg1, arg2, db_client: DatabaseClient
) -> Response:
    try:
        data_sources = quick_search_query(
            SearchParameters(search=arg1, location=arg2), db_client=db_client
        )

        return make_response(data_sources, HTTPStatus.OK.value)

    except Exception as e:
        user_message = "There was an error during the search operation"
        message = {
            "content": user_message
            + ": "
            + str(e)
            + "\n"
            + f"Search term: {arg1}\n"
            + f"Location: {arg2}"
        }
        post_to_webhook(json.dumps(message))

        return make_response(
            {"count": 0, "message": user_message},
            HTTPStatus.INTERNAL_SERVER_ERROR.value,
        )
