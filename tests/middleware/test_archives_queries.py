import psycopg2

from middleware.archives_queries import (
    archives_get_results,
    archives_get_query,
    ARCHIVES_GET_COLUMNS,
)
from tests.middleware.helper_functions import (
    insert_test_agencies_and_sources,
    has_expected_keys,
)
from tests.middleware.fixtures import (
    dev_db_connection,
    db_cursor,
    connection_with_test_data,
)


def test_archives_get_results(
    dev_db_connection: psycopg2.extensions.connection,
    db_cursor: psycopg2.extensions.cursor,
) -> None:
    """
    :param dev_db_connection: A connection to the development database.
    :param db_cursor: A cursor object for executing database queries.
    :return: This method does not return anything.

    This method tests the `archives_get_results` method by inserting a
    new record into the `data_sources` table in the development database
    and verifying that the number of results returned * by `archives_get_results`
    increases by 1.
    """
    original_results = archives_get_results(dev_db_connection)
    db_cursor.execute(
        """
        INSERT INTO data_sources(airtable_uid, source_url, name, update_frequency, url_status) 
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            "fake_uid",
            "https://www.fake_source_url.com",
            "fake_name",
            "Annually",
            "unbroken",
        ),
    )
    new_results = archives_get_results(dev_db_connection)
    assert len(new_results) == len(original_results) + 1


def test_archives_get_columns(
    connection_with_test_data: psycopg2.extensions.connection,
) -> None:
    """
    Test the archives_get_columns method, ensuring it properly returns an inserted source
    :param connection_with_test_data: A connection object to the database with test data.
    :return: None
    """
    results = archives_get_query(conn=connection_with_test_data)
    assert has_expected_keys(ARCHIVES_GET_COLUMNS, results[0].keys())
    for result in results:
        if result["id"] == "SOURCE_UID_1":
            return
