from typing import List, Dict, Any, Union
from psycopg2.extensions import connection as PgConnection
from utilities.common import convert_dates_to_strings

ARCHIVES_GET_COLUMNS = [
    "id",
    "source_url",
    "update_frequency",
    "last_cached",
]

def archives_get_results(conn: PgConnection) -> List[tuple]:
    """
    Fetches archive data based on specific criteria from the database.

    Parameters:
    - conn: A database connection object.

    Returns:
    - A list of tuples representing the fetched archive data.
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


def archives_get_query(test_query_results: List[Dict[str, Any]] = [], conn: Union[Dict, PgConnection] = {}) -> List[Dict[str, Any]]:
    """
    Retrieves and processes archive query results, either from test data or from the database.

    Parameters:
    - test_query_results: Optional test data to use instead of fetching from the database.
    - conn: A database connection object or a placeholder if using test data.

    Returns:
    - A list of dictionaries with clean archive data, including date conversion to string.
    """
    results = archives_get_results(conn) if not test_query_results else test_query_results
    archives_combined_results = [dict(zip(ARCHIVES_GET_COLUMNS, result)) for result in results]
    archives_combined_results_clean = [convert_dates_to_strings(item) for item in archives_combined_results]

    return archives_combined_results_clean


def archives_put_broken_as_of_results(id: str, broken_as_of: str, last_cached: str, conn: PgConnection) -> None:
    """
    Updates the database to mark a data source as broken as of a specific date.

    Parameters:
    - id: The ID of the data source.
    - broken_as_of: The date the source was marked as broken.
    - last_cached: The last cached date of the data source.
    - conn: A database connection object.

    Returns:
    - None
    """
    cursor = conn.cursor()
    sql_query = "UPDATE data_sources SET url_status = 'broken', broken_source_url_as_of = '{0}', last_cached = '{1}' WHERE airtable_uid = '{2}'"
    cursor.execute(sql_query.format(broken_as_of, last_cached, id))
    cursor.close()


def archives_put_last_cached_results(id: str, last_cached: str, conn: PgConnection) -> None:
    """
    Updates the last_cached date for a specific data source in the database.

    Parameters:
    - id: The ID of the data source.
    - last_cached: The new last cached date.
    - conn: A database connection object.

    Returns:
    - None
    """
    cursor = conn.cursor()
    sql_query = "UPDATE data_sources SET last_cached = '{0}' WHERE airtable_uid = '{1}'"
    cursor.execute(sql_query.format(last_cached, id))
    cursor.close()


def archives_put_query(id: str = "", broken_as_of: str = "", last_cached: str = "", conn: Union[Dict, PgConnection] = {}) -> None:
    """
    A higher-level function to update archive data based on whether a data source is broken or just needs a last_cached update.

    Parameters:
    - id: The ID of the data source to update.
    - broken_as_of: Optional date the source was marked as broken, if applicable.
    - last_cached: The new last cached date for the data source.
    - conn: A database connection object or a placeholder if using test data.

    Returns:
    - None
    """
    if broken_as_of:
        archives_put_broken_as_of_results(id, broken_as_of, last_cached, conn)
    else:
        archives_put_last_cached_results(id, last_cached, conn)

    conn.commit()
