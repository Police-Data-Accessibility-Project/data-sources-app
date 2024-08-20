from http import HTTPStatus
import json
from unittest.mock import MagicMock
from datetime import datetime

import psycopg2
import pytest

from middleware.quick_search_query import (
    quick_search_query,
    quick_search_query_wrapper,
    process_data_source_matches,
    SearchParameters,
    depluralize,
    DataSourceMatches,
)
from tests.helper_scripts.DynamicMagicMock import DynamicMagicMock

from tests.fixtures import connection_with_test_data, dev_db_connection


class QuickSearchQueryMocks(DynamicMagicMock):
    db_client: MagicMock
    process_search_parameters: MagicMock
    get_data_source_matches: MagicMock
    process_data_source_matches: MagicMock
    search_parameters: SearchParameters


def test_quick_search_query_logging(
    connection_with_test_data: psycopg2.extensions.connection,
) -> None:

    mock = QuickSearchQueryMocks(
        patch_root="middleware.quick_search_query",
        mocks_to_patch=[
            "process_search_parameters",
            "get_data_source_matches",
            "process_data_source_matches",
        ],
        return_values={
            "process_data_source_matches": DataSourceMatches(
                converted=[MagicMock(), MagicMock()], ids=[1, 2]
            ),
        },
    )

    data_sources = quick_search_query(
        search_parameters=mock.search_parameters,
        db_client=mock.db_client,
    )
    assert data_sources["count"] == 2
    assert (
        data_sources["data"] == mock.process_data_source_matches.return_value.converted
    )

    mock.process_search_parameters.assert_called_once_with(mock.search_parameters)
    mock.get_data_source_matches.assert_called_once_with(
        mock.db_client, mock.process_search_parameters.return_value
    )
    mock.process_data_source_matches.assert_called_once_with(
        mock.get_data_source_matches.return_value
    )
    mock.db_client.add_quick_search_log.assert_called_once_with(
        data_sources["count"],
        mock.process_data_source_matches.return_value,
        mock.process_search_parameters.return_value,
    )


class QuickSearchQueryWrapperMocks(DynamicMagicMock):
    db_client: MagicMock
    quick_search_query: MagicMock
    make_response: MagicMock
    post_to_webhook: MagicMock


@pytest.fixture
def mock_quick_search_query_wrapper(monkeypatch):
    mock = QuickSearchQueryWrapperMocks(
        patch_root="middleware.quick_search_query",
        mocks_to_patch=["quick_search_query", "make_response", "post_to_webhook"],
    )
    return mock


def call_and_validate_quick_search_query_wrapper(mock: QuickSearchQueryWrapperMocks):
    arg1 = "Source 1"
    arg2 = "City A"
    quick_search_query_wrapper(arg1=arg1, arg2=arg2, db_client=mock.db_client)
    mock.quick_search_query.assert_called_with(
        SearchParameters(search=arg1, location=arg2), db_client=mock.db_client
    )


def test_quick_search_query_wrapper_happy_path(mock_quick_search_query_wrapper):
    mock = mock_quick_search_query_wrapper
    mock.quick_search_query.return_value = [{"record_type": "Type A"}]

    call_and_validate_quick_search_query_wrapper(mock)

    mock.make_response.assert_called_with(
        [{"record_type": "Type A"}], HTTPStatus.OK
    )


def test_quick_search_query_wrapper_exception(mock_quick_search_query_wrapper):
    mock = mock_quick_search_query_wrapper
    mock.quick_search_query.side_effect = Exception("Test Exception")

    call_and_validate_quick_search_query_wrapper(mock)

    user_message = "There was an error during the search operation"
    mock.post_to_webhook.assert_called_with(
        json.dumps(
            {
                "content": "There was an error during the search operation: Test Exception\nSearch term: Source 1\nLocation: City A"
            }
        )
    )
    mock.make_response.assert_called_with(
        {"count": 0, "message": user_message}, HTTPStatus.INTERNAL_SERVER_ERROR
    )


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


@pytest.mark.parametrize(
    "term, expected",
    [
        ("apples oranges boxes", "apple orange box"),
        ("apple orange boxes", "apple orange box"),
        ("apples orange box", "apple orange box"),
        ("", ""),
    ],
)
def test_depluralize(term, expected):
    assert depluralize(term) == expected
