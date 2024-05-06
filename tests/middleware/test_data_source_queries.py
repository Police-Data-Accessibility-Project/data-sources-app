import psycopg2
import pytest

from app_test_data import DATA_SOURCES_ID_QUERY_RESULTS
from middleware.data_source_queries import (
    get_approved_data_sources,
    needs_identification_data_sources,
    data_source_by_id_results,
    data_sources_query,
    DATA_SOURCES_APPROVED_COLUMNS,
    data_source_by_id_query,
    get_data_sources_for_map,
)
from tests.middleware.helper_functions import (
    has_expected_keys,
    get_boolean_dictionary,
)
from tests.middleware.fixtures import connection_with_test_data, dev_db_connection


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
        name = result[0]
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
        name = result[0]
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
    assert has_expected_keys(result.keys(), DATA_SOURCES_ID_QUERY_RESULTS)
    assert result["agency_name"] == "Agency A"


def test_data_sources_query(
    connection_with_test_data: psycopg2.extensions.connection,
    inserted_data_sources_found: dict[str, bool],
) -> None:
    """
    Test that data sources query properly returns data for an inserted data source
    marked as 'approved', and none others.
    :param connection_with_test_data:
    :param inserted_data_sources_found:
    :return:
    """
    results = data_sources_query(connection_with_test_data)
    # Check that results include expected keys
    assert has_expected_keys(results[0].keys(), DATA_SOURCES_APPROVED_COLUMNS)
    for result in results:
        name = result["name"]
        if name in inserted_data_sources_found:
            inserted_data_sources_found[name] = True

    assert inserted_data_sources_found["Source 1"]
    assert not inserted_data_sources_found["Source 2"]
    assert not inserted_data_sources_found["Source 3"]


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
        name = result[1]
        if name == "Source 1":
            lat = result[8]
            lng = result[9]
            assert lat == 30 and lng == 20

        if name in inserted_data_sources_found:
            inserted_data_sources_found[name] = True
    assert inserted_data_sources_found["Source 1"]
    assert not inserted_data_sources_found["Source 2"]
    assert not inserted_data_sources_found["Source 3"]
