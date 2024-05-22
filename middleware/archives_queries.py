from typing import List, Dict, Any, Optional, Tuple
from utilities.common import convert_dates_to_strings
from psycopg2.extensions import connection as PgConnection


ARCHIVES_GET_COLUMNS = [
    "id",
    "source_url",
    "update_frequency",
    "last_cached",
]


def archives_get_results(conn: PgConnection) -> list[tuple[Any, ...]]:
    """
    Pulls data sources for the automatic archives script that performs caching

    :param conn: A psycopg2 connection object to a PostgreSQL database.
    :return: A list of dictionaries representing the rows matching the query conditions.
    """
    cursor = conn.cursor()
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
    test_query_results: Optional[List[Dict[str, Any]]] = None,
    conn: Optional[PgConnection] = None,
) -> List[Dict[str, Any]]:
    """
    Processes the archives get results, either from the database or a provided set of test results, and converts dates to strings.

    :param test_query_results: A list of dictionaries representing test query results, if any.
    :param conn: A psycopg2 connection object to a PostgreSQL database.
    :return: A list of dictionaries with the query results after processing and date conversion.
    """
    results = (
        archives_get_results(conn) if not test_query_results else test_query_results
    )
    archives_combined_results = [
        dict(zip(ARCHIVES_GET_COLUMNS, result)) for result in results
    ]
    archives_combined_results_clean = []
    for item in archives_combined_results:
        archives_combined_results_clean.append(convert_dates_to_strings(item))

    return archives_combined_results_clean


def archives_put_broken_as_of_results(
    id: str, broken_as_of: str, last_cached: str, conn: PgConnection
) -> None:
    """
    Updates the data_sources table setting the url_status to 'broken' for a given id.

    :param id: The airtable_uid of the data source.
    :param broken_as_of: The date when the source was identified as broken.
    :param last_cached: The last cached date of the data source.
    :param conn: A psycopg2 connection object to a PostgreSQL database.
    """
    cursor = conn.cursor()
    sql_query = "UPDATE data_sources SET url_status = 'broken', broken_source_url_as_of = '{0}', last_cached = '{1}' WHERE airtable_uid = '{2}'"
    cursor.execute(sql_query.format(broken_as_of, last_cached, id))
    cursor.close()


def archives_put_last_cached_results(
    id: str, last_cached: str, conn: PgConnection
) -> None:
    """
    Updates the last_cached field in the data_sources table for a given id.

    :param id: The airtable_uid of the data source.
    :param last_cached: The last cached date to be updated.
    :param conn: A psycopg2 connection object to a PostgreSQL database.
    """
    cursor = conn.cursor()
    sql_query = "UPDATE data_sources SET last_cached = '{0}' WHERE airtable_uid = '{1}'"
    cursor.execute(sql_query.format(last_cached, id))
    cursor.close()
