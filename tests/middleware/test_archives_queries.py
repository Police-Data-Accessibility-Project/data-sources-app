import datetime
import uuid
from http import HTTPStatus
from unittest.mock import MagicMock

import psycopg2
import pytest

from middleware.archives_queries import (
    archives_get_results,
    archives_get_query,
    ARCHIVES_GET_COLUMNS,
    archives_put_broken_as_of_results,
    archives_put_last_cached_results,
    update_archives_data,
)
from tests.helper_functions import (
    has_expected_keys,
    insert_test_data_source, DynamicMagicMock,
)
from tests.fixtures import (
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


def get_data_sources_archives_info(cursor, test_uid):
    cursor.execute(
        """
    SELECT URL_STATUS, BROKEN_SOURCE_URL_AS_OF, LAST_CACHED
    FROM PUBLIC.DATA_SOURCES
    WHERE AIRTABLE_UID = %s
    """,
        (test_uid,),
    )
    row = cursor.fetchone()
    return row


def test_archives_put_broken_as_of_results(
    dev_db_connection: psycopg2.extensions.connection,
) -> None:
    cursor = dev_db_connection.cursor()
    test_uid = insert_test_data_source(cursor)

    # Check data properly inserted
    row = get_data_sources_archives_info(cursor, test_uid)
    assert row[0] == "available"
    assert row[1] is None
    assert row[2] is None

    broken_as_of_date = datetime.datetime.now().strftime("%Y-%m-%d")
    last_cached = datetime.datetime.now().strftime("%Y-%m-%d")

    archives_put_broken_as_of_results(
        id=test_uid,
        broken_as_of=broken_as_of_date,
        last_cached=last_cached,
        cursor=cursor,
    )

    row = get_data_sources_archives_info(cursor, test_uid)
    assert row[0] == "broken"
    assert str(row[1]) == broken_as_of_date
    assert str(row[2]) == last_cached


def test_archives_put_last_cached_results(
    dev_db_connection: psycopg2.extensions.connection,
):
    cursor = dev_db_connection.cursor()
    test_uid = insert_test_data_source(cursor)

    # Check data properly inserted
    row = get_data_sources_archives_info(cursor, test_uid)
    assert row[0] == "available"
    assert row[1] is None
    assert row[2] is None

    last_cached = datetime.datetime(year=1999, month=5, day=30).strftime("%Y-%m-%d")
    archives_put_last_cached_results(
        id=test_uid, last_cached=last_cached, cursor=cursor
    )
    row = get_data_sources_archives_info(cursor, test_uid)
    assert row[0] == "available"
    assert row[1] is None
    assert str(row[2]) == last_cached


class UpdateArchivesDataMocks(DynamicMagicMock):
    cursor: MagicMock
    data_id: MagicMock
    last_cached: MagicMock
    broken_as_of: MagicMock
    archives_put_broken_as_of_results: MagicMock
    archives_put_last_cached_results: MagicMock
    make_response: MagicMock


@pytest.fixture
def setup_update_archives_data_mocks(monkeypatch):
    mock = UpdateArchivesDataMocks()

    monkeypatch.setattr(
        "middleware.archives_queries.archives_put_broken_as_of_results",
        mock.archives_put_broken_as_of_results,
    )
    monkeypatch.setattr(
        "middleware.archives_queries.archives_put_last_cached_results",
        mock.archives_put_last_cached_results,
    )
    monkeypatch.setattr(
        "middleware.archives_queries.make_response", mock.make_response
    )
    return mock

def test_update_archives_data_broken_as_of(setup_update_archives_data_mocks):
    mock = setup_update_archives_data_mocks

    update_archives_data(mock.cursor, mock.data_id, mock.last_cached, mock.broken_as_of)

    mock.archives_put_broken_as_of_results.assert_called_with(
        mock.data_id,
        mock.broken_as_of,
        mock.last_cached,
        mock.cursor
    )
    mock.archives_put_last_cached_results.assert_not_called()
    mock.make_response.assert_called_with(
        {"status": "success"}, HTTPStatus.OK
    )

def test_update_archives_data_not_broken_as_of(setup_update_archives_data_mocks):
    mock = setup_update_archives_data_mocks

    update_archives_data(mock.cursor, mock.data_id, mock.last_cached, None)

    mock.archives_put_broken_as_of_results.assert_not_called()
    mock.archives_put_last_cached_results.assert_called_with(
        mock.data_id,
        mock.last_cached,
        mock.cursor
    )
    mock.make_response.assert_called_with(
        {"status": "success"}, HTTPStatus.OK
    )


