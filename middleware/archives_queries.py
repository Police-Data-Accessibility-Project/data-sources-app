from http import HTTPStatus
from typing import List, Dict, Any, Optional, Tuple

import psycopg2
from flask import make_response

from utilities.common import convert_dates_to_strings
from psycopg2.extensions import connection as PgConnection


ARCHIVES_GET_COLUMNS = [
    "id",
    "source_url",
    "update_frequency",
    "last_cached",
]


# DatabaseClient.get_data_sources_to_archive()
def archives_get_results(cursor: psycopg2.extensions.cursor) -> list[tuple[Any, ...]]:
    """
    Pulls data sources for the automatic archives script that performs caching

    :param cursor: A psycopg2 cursor object to a PostgreSQL database.
    :return: A list of dictionaries representing the rows matching the query conditions.
    """
    sql_query = """
    SELECT
        airtable_uid,
        source_url,
        update_frequency,
        last_cached,
        broken_source_url_as_of
    FROM
        data_sources
    WHERE 
        (last_cached IS NULL OR update_frequency IS NOT NULL) AND broken_source_url_as_of IS NULL AND url_status <> 'broken' AND source_url IS NOT NULL
    """
    cursor.execute(sql_query)

    return cursor.fetchall()


def archives_get_query(
    cursor: psycopg2.extensions.cursor,
) -> List[Dict[str, Any]]:
    """
    Processes the archives get results, either from the database and converts dates to strings.

    :param cursor: A psycopg2 cursor object to a PostgreSQL database.
    :return: A list of dictionaries with the query results after processing and date conversion.
    """
    # TODO: replace with DatabaseClient method get_data_sources_to_archive()
    results = archives_get_results(cursor)
    archives_combined_results = [
        dict(zip(ARCHIVES_GET_COLUMNS, result)) for result in results
    ]
    archives_combined_results_clean = []
    for item in archives_combined_results:
        archives_combined_results_clean.append(convert_dates_to_strings(item))

    return archives_combined_results_clean


# DatabaseClient.update_url_status_to_broken()
def archives_put_broken_as_of_results(
    id: str, broken_as_of: str, last_cached: str, cursor: psycopg2.extensions.cursor
) -> None:
    """
    Updates the data_sources table setting the url_status to 'broken' for a given id.

    :param id: The airtable_uid of the data source.
    :param broken_as_of: The date when the source was identified as broken.
    :param last_cached: The last cached date of the data source.
    :param conn: A psycopg2 connection object to a PostgreSQL database.
    """
    sql_query = """
    UPDATE data_sources 
    SET 
        url_status = 'broken', 
        broken_source_url_as_of = %s, 
        last_cached = %s 
        WHERE airtable_uid = %s
    """
    cursor.execute(sql_query, (broken_as_of, last_cached, id))


def archives_put_last_cached_results(
    id: str, last_cached: str, cursor: psycopg2.extensions.cursor
) -> None:
    """
    Updates the last_cached field in the data_sources table for a given id.

    :param cursor:
    :param id: The airtable_uid of the data source.
    :param last_cached: The last cached date to be updated.
    """
    sql_query = "UPDATE data_sources SET last_cached = %s WHERE airtable_uid = %s"
    cursor.execute(sql_query, (last_cached, id))


def update_archives_data(
    cursor: psycopg2.extensions.cursor,
    data_id: str,
    last_cached: str,
    broken_as_of: str,
):
    """
    Processes a request to update the data source

    :param cursor: A psycopg2 cursor object to a PostgreSQL database.
    :param data_id:
    :param last_cached:
    :param broken_as_of:
    :return: A dictionary containing a message about the update operation
    """
    if broken_as_of:
        # TODO: replace with DatabaseClient method update_url_status_to_broken()
        archives_put_broken_as_of_results(data_id, broken_as_of, last_cached, cursor)
    else:
        archives_put_last_cached_results(data_id, last_cached, cursor)

    return make_response({"status": "success"}, HTTPStatus.OK)
