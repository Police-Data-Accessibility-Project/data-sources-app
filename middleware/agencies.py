from http import HTTPStatus

import psycopg2
import psycopg2.extras
from flask import Response, make_response

from utilities.common import convert_dates_to_strings

AGENCY_SELECT_QUERY = """
    SELECT 
        name,
        homepage_url,
        count_data_sources,
        agency_type,
        multi_agency,
        submitted_name,
        jurisdiction_type,
        state_iso,
        municipality,
        zip_code,
        county_fips,
        county_name,
        lat,
        lng,
        data_sources,
        no_web_presence,
        airtable_agency_last_modified,
        data_sources_last_updated,
        approved,
        rejection_reason,
        last_approval_editor,
        agency_created,
        county_airtable_uid,
        defunct_year,
        airtable_uid
    FROM agencies where approved = 'TRUE' limit 1000 offset %s
    """


def get_agencies(cursor: psycopg2.extras.RealDictCursor, page: int) -> Response:
    """
    Retrieves a paginated list of approved agencies from the database.

    :param cursor: A cursor object from a psycopg2 connection.
    :param page: The page number of results to return.
    :return: A response object with the relevant agency information and status code.
    """
    agencies_matches = get_agencies_matches(cursor, page)
    agencies = {"count": len(agencies_matches), "data": agencies_matches}
    return make_response(agencies, HTTPStatus.OK)


def get_agencies_matches(cursor: psycopg2.extras.RealDictCursor, page: int):
    """
    Retrieves a paginated list of approved agencies from the database.
    Args:
        cursor (psycopg2.extras.RealDictCursor): A cursor object from a psycopg2 connection.
        page (int): The page number of results to return.
    Returns:
        list: A list of dictionaries containing the relevant agency information.
    """
    results = execute_agency_query(cursor, page)
    return process_results(results)


def process_results(results: list[dict]) -> list[dict]:
    """
    Processes the results by converting dates in each dictionary to strings.
    Args:
        results (list[dict]): A list of dictionaries containing the results.
    Returns:
        list[dict]: The processed list of dictionaries with converted dates.
    """
    for result in results:
        convert_dates_to_strings(result)
    return results


def execute_agency_query(cursor: psycopg2.extras.RealDictCursor, page: int):
    offset = get_offset(page)
    cursor.execute(
        AGENCY_SELECT_QUERY,
        (offset,),
    )
    results = cursor.fetchall()
    return results


def get_offset(page: int) -> int:
    """
    Calculates the offset value for pagination based on the given page number.
    Args:
        page (int): The page number for which the offset is to be calculated.
    Returns:
        int: The calculated offset value.
    Example:
        >>> get_offset(3)
        2000
    """
    return (page - 1) * 1000
