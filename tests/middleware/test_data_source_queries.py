from unittest.mock import MagicMock

import psycopg2
import pytest

from middleware import data_source_queries
from middleware.data_source_queries import (
    get_approved_data_sources,
    needs_identification_data_sources,
    data_source_by_id_results,
    data_source_by_id_query,
    get_data_sources_for_map,
    data_source_by_id_wrapper,
)
from tests.helper_functions import (
    get_boolean_dictionary,
)
from tests.fixtures import connection_with_test_data, dev_db_connection


@pytest.fixture
def inserted_data_sources_found():
    """
    A boolean dictionary for identifying if test data sources have been found
    :return: boolean dictionary with test data source names as keys,
        all values initialized to false
    """
    return get_boolean_dictionary(("Source 1", "Source 2", "Source 3"))


def test_get_approved_data_sources(
    connection_with_test_data: psycopg2.extensions.connection,
    inserted_data_sources_found: dict[str, bool],
) -> None:
    """
    Test that only one data source -- one set to approved -- is returned by 'get_approved_data_sources
    :param connection_with_test_data:
    :param inserted_data_sources_found:
    :return:
    """
    results = get_approved_data_sources(conn=connection_with_test_data)

    for result in results:
        name = result["name"]
        if name in inserted_data_sources_found:
            inserted_data_sources_found[name] = True

    assert inserted_data_sources_found["Source 1"]
    assert not inserted_data_sources_found["Source 2"]
    assert not inserted_data_sources_found["Source 3"]


def test_needs_identification(
    connection_with_test_data: psycopg2.extensions.connection,
    inserted_data_sources_found: dict[str, bool],
) -> None:
    """
    Test only source marked as 'Needs Identification' is returned by 'needs_identification_data_sources'
    :param connection_with_test_data:
    :param inserted_data_sources_found:
    :return:
    """
    results = needs_identification_data_sources(conn=connection_with_test_data)
    for result in results:
        name = result["name"]
        if name in inserted_data_sources_found:
            inserted_data_sources_found[name] = True

    assert not inserted_data_sources_found["Source 1"]
    assert inserted_data_sources_found["Source 2"]
    assert not inserted_data_sources_found["Source 3"]


def test_data_source_by_id_results(
    connection_with_test_data: psycopg2.extensions.connection,
) -> None:
    """
    Test that data_source_by_id properly returns data for an inserted data source
    -- and does not return one which was not inserted
    :param connection_with_test_data:
    :return:
    """
    # Insert other data sources as well with different id
    result = data_source_by_id_results(
        data_source_id="SOURCE_UID_1", conn=connection_with_test_data
    )
    assert result
    # Check that a data source which was not inserted is not pulled
    result = data_source_by_id_results(
        data_source_id="SOURCE_UID_4", conn=connection_with_test_data
    )
    assert not result


def test_data_source_by_id_query(
    connection_with_test_data: psycopg2.extensions.connection,
) -> None:
    """
    Test that data_source_by_id_query properly returns data for an inserted data source
    -- and does not return one which was not inserted
    :param connection_with_test_data:
    :return:
    """
    result = data_source_by_id_query(
        data_source_id="SOURCE_UID_1", conn=connection_with_test_data
    )
    assert result["agency_name"] == "Agency A"


def test_get_data_sources_for_map(
    connection_with_test_data: psycopg2.extensions.connection,
    inserted_data_sources_found: dict[str, bool],
) -> None:
    """
    Test that get_data_sources_for_map includes only the expected source
    with the expected lat/lng coordinates
    :param connection_with_test_data:
    :param inserted_data_sources_found:
    :return:
    """
    results = get_data_sources_for_map(conn=connection_with_test_data)
    for result in results:
        name = result["name"]
        if name == "Source 1":
            assert result["lat"] == 30 and result["lng"] == 20

        if name in inserted_data_sources_found:
            inserted_data_sources_found[name] = True
    assert inserted_data_sources_found["Source 1"]
    assert not inserted_data_sources_found["Source 2"]
    assert not inserted_data_sources_found["Source 3"]


def test_convert_data_source_matches():
    """
    Convert_data_source_matches should output a list of
    dictionaries based on the provided list of columns
    and the list of tuples
    """

    # Define Test case Input and Output data
    testcases = [
        {
            "data_source_output_columns": ["name", "age"],
            "results": [("Joe", 20), ("Annie", 30)],
            "output": [{"name": "Joe", "age": 20}, {"name": "Annie", "age": 30}],
        },
        # You can add more tests here as per requirement.
    ]

    # Execute the tests
    for testcase in testcases:
        assert (
            data_source_queries.convert_data_source_matches(
                testcase["data_source_output_columns"], testcase["results"]
            )
            == testcase["output"]
        )


@pytest.fixture
def mock_make_response(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr("middleware.data_source_queries.make_response", mock)
    return mock


@pytest.fixture
def mock_data_source_by_id_query(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr("middleware.data_source_queries.data_source_by_id_query", mock)
    return mock


def test_data_source_by_id_wrapper_data_found(mock_data_source_by_id_query, mock_make_response):
    mock_data_source_by_id_query.return_value = {"agency_name": "Agency A"}
    mock_conn = MagicMock()
    data_source_by_id_wrapper(arg="SOURCE_UID_1", conn=mock_conn)
    mock_data_source_by_id_query.assert_called_with(
        data_source_id="SOURCE_UID_1", conn=mock_conn
    )
    mock_make_response.assert_called_with({"agency_name": "Agency A"}, 200)

def test_data_source_by_id_wrapper_data_not_found(mock_data_source_by_id_query, mock_make_response):
    mock_data_source_by_id_query.return_value = None
    mock_conn = MagicMock()
    data_source_by_id_wrapper(arg="SOURCE_UID_1", conn=mock_conn)
    mock_data_source_by_id_query.assert_called_with(
        data_source_id="SOURCE_UID_1", conn=mock_conn
    )
    mock_make_response.assert_called_with({"message": "Data source not found."}, 200)