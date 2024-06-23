from collections import namedtuple

import psycopg2
import spacy
import json
import datetime
from http import HTTPStatus

from flask import make_response, Response

from middleware.webhook_logic import post_to_webhook
from utilities.common import convert_dates_to_strings, format_arrays
from typing import List, Dict, Any
from psycopg2.extensions import cursor as PgCursor

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

QUICK_SEARCH_SQL = """
    SELECT
        data_sources.airtable_uid,
        data_sources.name AS data_source_name,
        data_sources.description,
        data_sources.record_type,
        data_sources.source_url,
        data_sources.record_format,
        data_sources.coverage_start,
        data_sources.coverage_end,
        data_sources.agency_supplied,
        agencies.name AS agency_name,
        agencies.municipality,
        agencies.state_iso
    FROM
        agency_source_link
    INNER JOIN
        data_sources ON agency_source_link.airtable_uid = data_sources.airtable_uid
    INNER JOIN
        agencies ON agency_source_link.agency_described_linked_uid = agencies.airtable_uid
    INNER JOIN
        state_names ON agencies.state_iso = state_names.state_iso
    WHERE
        (data_sources.name LIKE '%{0}%' OR data_sources.description LIKE '%{0}%' OR data_sources.record_type LIKE '%{0}%' OR data_sources.tags LIKE '%{0}%') 
        AND (agencies.county_name LIKE '%{1}%' OR substr(agencies.county_name,3,length(agencies.county_name)-4) || ' County' LIKE '%{1}%' 
            OR agencies.state_iso LIKE '%{1}%' OR agencies.municipality LIKE '%{1}%' OR agencies.agency_type LIKE '%{1}%' OR agencies.jurisdiction_type LIKE '%{1}%' 
            OR agencies.name LIKE '%{1}%' OR state_names.state_name LIKE '%{1}%')
        AND data_sources.approval_status = 'approved'
        AND data_sources.url_status not in ('broken', 'none found')

"""

INSERT_LOG_QUERY = """
    INSERT INTO quick_search_query_logs 
    (search, location, results, result_count) 
    VALUES (%s, %s, %s, %s)
    """


def unaltered_search_query(
    cursor: PgCursor, search: str, location: str
) -> List[Dict[str, Any]]:
    """
    Executes the quick search SQL query with unaltered search and location terms.

    :param cursor: A cursor object from a psycopg2 connection.
    :param search: The search term entered by the user.
    :param location: The location term entered by the user.
    :return: A list of dictionaries representing the search results.
    """
    print(f"Query parameters: '%{search}%', '%{location}%'")
    cursor.execute(QUICK_SEARCH_SQL.format(search.title(), location.title()))
    results = cursor.fetchall()

    return results


def spacy_search_query(
    cursor: PgCursor, search: str, location: str
) -> List[Dict[str, Any]]:
    """
    Executes the quick search SQL query with depluralized (lemmatized) search and location terms using spaCy.

    :param cursor: A cursor object from a psycopg2 connection.
    :param search: The search term entered by the user.
    :param location: The location term entered by the user.
    :return: A list of dictionaries representing the search results.
    """
    # Depluralize search term to increase match potential
    depluralized_search_term = depluralize(search)
    location = location.strip()

    print(f"Query parameters: '%{depluralized_search_term}%', '%{location}%'")

    cursor.execute(
        QUICK_SEARCH_SQL.format(depluralized_search_term.title(), location.title())
    )
    results = cursor.fetchall()

    return results


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
    cursor: PgCursor = None,
) -> Dict[str, Any]:
    """
    Performs a quick search using both unaltered and lemmatized search terms, returning the more fruitful result set.

    :param search_parameters:

    :param cursor: A psycopg2 cursor to the database.
    :return: A dictionary with the count of results and the data itself.
    """

    processed_search_parameters = process_search_parameters(search_parameters)

    data_source_matches = get_data_source_matches(cursor, processed_search_parameters)
    processed_data_source_matches = process_data_source_matches(data_source_matches)

    data_sources = {
        "count": len(processed_data_source_matches.converted),
        "data": processed_data_source_matches.converted,
    }

    log_query(
        cursor,
        data_sources["count"],
        processed_data_source_matches,
        processed_search_parameters,
    )

    return data_sources


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
    cursor: PgCursor, sp: SearchParameters
) -> List[Dict[str, Any]]:
    unaltered_results = unaltered_search_query(cursor, sp.search, sp.location)
    spacy_results = spacy_search_query(cursor, sp.search, sp.location)
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
    arg1, arg2, cursor: psycopg2.extensions.cursor
) -> Response:
    try:
        data_sources = quick_search_query(
            SearchParameters(search=arg1, location=arg2), cursor=cursor
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
