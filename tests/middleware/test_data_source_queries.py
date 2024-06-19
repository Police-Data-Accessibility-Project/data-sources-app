from datetime import datetime
from http import HTTPStatus
from unittest.mock import MagicMock, patch

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
    create_data_source_update_query,
    update_data_source,
    create_new_data_source_query,
    add_new_data_source,
)
from middleware.login_queries import try_logging_in
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


def test_create_data_source_update_query():
    data = {
        "name": "New Name",
        "description": "New Description",
        "rejection_note": "Rejected",
        "data_source_request": "Requested",
        "approval_status": "Approved",
        "airtable_uid": "12345",
        "airtable_source_last_modified": "2022-01-01",
    }
    data_source_id = "12345"
    expected_query = """
    UPDATE data_sources 
    SET name = 'New Name', description = 'New Description'
    WHERE airtable_uid = '12345'
    """
    assert create_data_source_update_query(data, data_source_id) == expected_query


def test_create_data_source_update_query_with_integer():
    data = {
        "age": 25,
        "rejection_note": "Rejected",
        "data_source_request": "Requested",
        "approval_status": "Approved",
        "airtable_uid": "12345",
        "airtable_source_last_modified": "2022-01-01",
    }
    data_source_id = "12345"
    expected_query = """
    UPDATE data_sources 
    SET age = 25
    WHERE airtable_uid = '12345'
    """
    assert create_data_source_update_query(data, data_source_id) == expected_query


def test_create_data_source_update_query_with_empty_data():
    data = {}
    data_source_id = "12345"
    expected_query = """
    UPDATE data_sources 
    SET 
    WHERE airtable_uid = '12345'
    """
    assert create_data_source_update_query(data, data_source_id) == expected_query


def test_update_data_source(monkeypatch):
    # Create Mock values
    mock_cursor = MagicMock()
    mock_data = MagicMock()
    mock_data_source_id = MagicMock()
    mock_sql_query = MagicMock()
    mock_create_data_source_update_query = MagicMock(return_value=mock_sql_query)
    mock_make_response = MagicMock()
    # Use monkeypatch to set mock values
    monkeypatch.setattr(
        "middleware.data_source_queries.create_data_source_update_query",
        mock_create_data_source_update_query,
    )
    monkeypatch.setattr(
        "middleware.data_source_queries.make_response", mock_make_response
    )
    # Call function
    update_data_source(mock_cursor, mock_data, mock_data_source_id)

    # Assert
    mock_create_data_source_update_query.assert_called_with(
        mock_data, mock_data_source_id
    )
    mock_cursor.execute.assert_called_with(mock_sql_query)
    mock_make_response.assert_called_with(
        {"message": "Data source updated successfully."}, HTTPStatus.OK
    )


def setup_try_logging_in_mocks(monkeypatch, check_password_hash_return_value):
    # Create Mock values
    mock_cursor = MagicMock()
    mock_email = MagicMock()
    mock_password = MagicMock()
    mock_password_digest = MagicMock()
    mock_user_id = MagicMock()
    mock_session_token = MagicMock()
    mock_user_info = {
        "password_digest": mock_password_digest,
        "id": mock_user_id,
    }
    mock_get_user_info = MagicMock(return_value=mock_user_info)
    mock_make_response = MagicMock()
    mock_create_session_token = MagicMock(return_value=mock_session_token)
    mock_check_password_hash = MagicMock(return_value=check_password_hash_return_value)

    # Use monkeypatch to set mock values
    monkeypatch.setattr(
        "middleware.login_queries.create_session_token",
        mock_create_session_token,
    )
    monkeypatch.setattr("middleware.login_queries.make_response", mock_make_response)
    monkeypatch.setattr("middleware.login_queries.get_user_info", mock_get_user_info)
    monkeypatch.setattr(
        "middleware.login_queries.check_password_hash", mock_check_password_hash
    )

    return (
        mock_cursor,
        mock_email,
        mock_password,
        mock_user_id,
        mock_session_token,
        mock_get_user_info,
        mock_make_response,
        mock_create_session_token,
    )


def test_try_logging_in_successful(monkeypatch):
    (
        mock_cursor,
        mock_email,
        mock_password,
        mock_user_id,
        mock_session_token,
        mock_get_user_info,
        mock_make_response,
        mock_create_session_token,
    ) = setup_try_logging_in_mocks(monkeypatch, check_password_hash_return_value=True)

    # Call function
    try_logging_in(mock_cursor, mock_email, mock_password)

    # Assert
    mock_get_user_info.assert_called_with(mock_cursor, mock_email)
    mock_create_session_token.assert_called_with(mock_cursor, mock_user_id, mock_email)
    mock_make_response.assert_called_with(
        {"message": "Successfully logged in", "data": mock_session_token}, HTTPStatus.OK
    )


def test_try_logging_in_unsuccessful(monkeypatch):
    (
        mock_cursor,
        mock_email,
        mock_password,
        mock_user_id,
        mock_session_token,
        mock_get_user_info,
        mock_make_response,
        mock_create_session_token,
    ) = setup_try_logging_in_mocks(monkeypatch, check_password_hash_return_value=False)

    # Call function
    try_logging_in(mock_cursor, mock_email, mock_password)

    # Assert
    mock_get_user_info.assert_called_with(mock_cursor, mock_email)
    mock_create_session_token.assert_not_called()
    mock_make_response.assert_called_with(
        {"message": "Invalid email or password"}, HTTPStatus.UNAUTHORIZED
    )


def test_add_new_data_source(monkeypatch):
    # Create Mock values
    mock_cursor = MagicMock()
    mock_data = MagicMock()
    mock_sql_query = MagicMock()
    mock_create_new_data_source_query = MagicMock(return_value=mock_sql_query)
    mock_make_response = MagicMock()
    # Use monkeypatch to set mock values
    monkeypatch.setattr(
        "middleware.data_source_queries.create_new_data_source_query",
        mock_create_new_data_source_query,
    )
    monkeypatch.setattr(
        "middleware.data_source_queries.make_response", mock_make_response
    )
    # Call function
    add_new_data_source(mock_cursor, mock_data)

    # Assert
    mock_create_new_data_source_query.assert_called_with(mock_data)
    mock_cursor.execute.assert_called_with(mock_sql_query)
    mock_make_response.assert_called_with(
        {"message": "Data source added successfully."}, HTTPStatus.OK
    )


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


@pytest.fixture
def mock_get_restricted_columns():
    with patch("middleware.data_source_queries.get_restricted_columns") as mock:
        mock.return_value = ["restricted_column1", "restricted_column2"]
        yield mock


@pytest.fixture
def mock_uuid():
    with patch("middleware.data_source_queries.uuid") as mock:
        mock.uuid4.return_value = "123e4567-e89b-12d3-a456-426655440000"
        yield mock


@pytest.fixture
def mock_datetime():
    with patch("middleware.data_source_queries.datetime") as mock:
        mock.now.return_value = datetime(2022, 1, 1)
        yield mock


def test_create_new_data_source_query(
    mock_get_restricted_columns, mock_uuid, mock_datetime
):
    data = {"column1": "value1", "column2": 123, "column3": True}
    expected_sql_query = (
        "INSERT INTO data_sources "
        "(column1, column2, column3, approval_status, url_status, data_source_created, airtable_uid) "
        "VALUES ('value1', 123, True, False, '[\"ok\"]', '2022-01-01', '123e4567-e89b-12d3-a456-426655440000') "
        "RETURNING *"
    )

    result = create_new_data_source_query(data)

    assert result == expected_sql_query
    mock_get_restricted_columns.assert_called_once()
    mock_uuid.uuid4.assert_called_once()
    mock_datetime.now.assert_called_once()


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


def test_data_source_by_id_wrapper_data_found(
    mock_data_source_by_id_query, mock_make_response
):
    mock_data_source_by_id_query.return_value = {"agency_name": "Agency A"}
    mock_conn = MagicMock()
    data_source_by_id_wrapper(arg="SOURCE_UID_1", conn=mock_conn)
    mock_data_source_by_id_query.assert_called_with(
        data_source_id="SOURCE_UID_1", conn=mock_conn
    )
    mock_make_response.assert_called_with({"agency_name": "Agency A"}, 200)


def test_data_source_by_id_wrapper_data_not_found(
    mock_data_source_by_id_query, mock_make_response
):
    mock_data_source_by_id_query.return_value = None
    mock_conn = MagicMock()
    data_source_by_id_wrapper(arg="SOURCE_UID_1", conn=mock_conn)
    mock_data_source_by_id_query.assert_called_with(
        data_source_id="SOURCE_UID_1", conn=mock_conn
    )
    mock_make_response.assert_called_with({"message": "Data source not found."}, 200)
