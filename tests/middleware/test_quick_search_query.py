import json
from unittest.mock import MagicMock
from datetime import datetime
from unittest.mock import patch

import psycopg2
import pytest

from middleware.quick_search_query import (
    unaltered_search_query,
    quick_search_query,
    QUICK_SEARCH_COLUMNS,
    quick_search_query_wrapper,
    process_data_source_matches,
    SearchParameters,
    depluralize,
)
from tests.helper_functions import (
    has_expected_keys,
    get_most_recent_quick_search_query_log,
)
from tests.fixtures import connection_with_test_data, dev_db_connection


def test_unaltered_search_query(
    connection_with_test_data: psycopg2.extensions.connection,
) -> None:
    """
    :param connection_with_test_data: A connection object that is connected to the test database containing the test data.
    :return: None
    Test the unaltered_search_query method properly returns only one result
    """
    response = unaltered_search_query(
        connection_with_test_data.cursor(), search="Source 1", location="City A"
    )

    assert len(response) == 1
    assert response[0][3] == "Type A"  # Record Type


def test_quick_search_query_logging(
    connection_with_test_data: psycopg2.extensions.connection,
) -> None:
    """
    Tests that quick_search_query properly creates a log of the query

    :param connection_with_test_data: psycopg2.extensions.connection object representing the connection to the test database.
    :return: None
    """
    # Get datetime of test
    with connection_with_test_data.cursor() as cursor:
        cursor.execute("SELECT NOW()")
        result = cursor.fetchone()
        test_datetime = result[0]

        quick_search_query(
            SearchParameters(search="Source 1", location="City A"), cursor=cursor
        )
        # Test that query inserted into log
        result = get_most_recent_quick_search_query_log(cursor, "Source 1", "City A")
    assert result.result_count == 1
    assert len(result.results) == 1
    assert result.results[0] == "SOURCE_UID_1"
    assert result.updated_at >= test_datetime


def test_quick_search_query_results(
    connection_with_test_data: psycopg2.extensions.connection,
) -> None:
    """
    Test the `quick_search_query` method returns expected test data

    :param connection_with_test_data: The connection to the test data database.
    :return: None
    """
    with connection_with_test_data.cursor() as cursor:
        results = quick_search_query(
            SearchParameters(search="Source 1", location="City A"), cursor=cursor
        )
        # Test that results include expected keys
        assert has_expected_keys(results["data"][0].keys(), QUICK_SEARCH_COLUMNS)
        assert len(results["data"]) == 1
        assert results["data"][0]["record_type"] == "Type A"
        # "Source 3" was listed as pending and shouldn't show up
        results = quick_search_query(
            SearchParameters(search="Source 3", location="City C"), cursor=cursor
        )
        assert len(results["data"]) == 0


def test_quick_search_query_no_results(
    connection_with_test_data: psycopg2.extensions.connection,
) -> None:
    """
    Test the `quick_search_query` method returns no results when there are no matches

    :param connection_with_test_data: The connection to the test data database.
    :return: None
    """
    results = quick_search_query(
        SearchParameters(
            search="Nonexistent Source",
            location="Nonexistent Location",
        ),
        cursor=connection_with_test_data.cursor(),
    )
    assert len(results["data"]) == 0


@pytest.fixture
def mock_quick_search_query(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr("middleware.quick_search_query.quick_search_query", mock)
    return mock


@pytest.fixture
def mock_make_response(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr("middleware.quick_search_query.make_response", mock)
    return mock


@pytest.fixture
def mock_post_to_webhook(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr("middleware.quick_search_query.post_to_webhook", mock)
    return mock


def test_quick_search_query_wrapper_happy_path(
    mock_quick_search_query, mock_make_response
):
    mock_quick_search_query.return_value = [{"record_type": "Type A"}]
    mock_cursor = MagicMock()
    quick_search_query_wrapper(arg1="Source 1", arg2="City A", cursor=mock_cursor)
    mock_quick_search_query.assert_called_with(
        SearchParameters(search="Source 1", location="City A"), cursor=mock_cursor
    )
    mock_make_response.assert_called_with([{"record_type": "Type A"}], 200)


def test_quick_search_query_wrapper_exception(
    mock_quick_search_query, mock_make_response, mock_post_to_webhook
):
    mock_quick_search_query.side_effect = Exception("Test Exception")
    arg1 = "Source 1"
    arg2 = "City A"
    mock_cursor = MagicMock()
    quick_search_query_wrapper(arg1=arg1, arg2=arg2, cursor=mock_cursor)
    mock_quick_search_query.assert_called_with(
        SearchParameters(search=arg1, location=arg2), cursor=mock_cursor
    )
    user_message = "There was an error during the search operation"
    mock_post_to_webhook.assert_called_with(
        json.dumps(
            {
                "content": "There was an error during the search operation: Test Exception\nSearch term: Source 1\nLocation: City A"
            }
        )
    )
    mock_make_response.assert_called_with({"count": 0, "message": user_message}, 500)


# Test cases
@pytest.fixture
def sample_data_source_matches():
    return [
        {
            "airtable_uid": "id1",
            "field1": "value1",
            "field_datetime": datetime(2020, 1, 1),
            "field_array": '["abc","def"]',
        },
        {
            "airtable_uid": "id2",
            "field2": "value2",
            "field_datetime": datetime(2021, 2, 2),
            "field_array": '["hello, world"]',
        },
    ]


def test_process_data_source_matches(sample_data_source_matches):
    expected_converted = [
        {
            "airtable_uid": "id1",
            "field1": "value1",
            "field_datetime": "2020-01-01",
            "field_array": ["abc", "def"],
        },
        {
            "airtable_uid": "id2",
            "field2": "value2",
            "field_datetime": "2021-02-02",
            "field_array": ["hello, world"],
        },
    ]
    expected_ids = ["id1", "id2"]

    result = process_data_source_matches(sample_data_source_matches)

    assert result.converted == expected_converted
    assert result.ids == expected_ids


def test_depluralize_with_plural_words():
    term = "apples oranges boxes"
    expected = "apple orange box"
    assert depluralize(term) == expected


def test_depluralize_with_singular_words():
    term = "apple orange box"
    expected = "apple orange box"
    assert depluralize(term) == expected


def test_depluralize_with_mixed_words():
    term = "apples orange box"
    expected = "apple orange box"
    assert depluralize(term) == expected


def test_depluralize_with_empty_string():
    term = ""
    expected = ""
    assert depluralize(term) == expected
