from datetime import datetime
from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest

from database_client.database_client import DatabaseClient
from middleware import data_source_queries
from middleware.data_source_queries import (
    data_source_by_id_wrapper,
    DataSourceNotFoundError,
)
from middleware.login_queries import try_logging_in
from tests.helper_scripts.DymamicMagicMock import DynamicMagicMock
from tests.helper_scripts.helper_functions import (
    get_boolean_dictionary,
)


@pytest.fixture
def inserted_data_sources_found():
    """
    A boolean dictionary for identifying if test data sources have been found
    :return: boolean dictionary with test data source names as keys,
        all values initialized to false
    """
    return get_boolean_dictionary(("Source 1", "Source 2", "Source 3"))


class TryLoggingInMocks(DynamicMagicMock):
    db_client: MagicMock
    email: MagicMock
    password: MagicMock
    password_digest: MagicMock
    user_id: MagicMock
    user_info: MagicMock
    check_password_hash: MagicMock
    unauthorized_response: MagicMock
    login_response: MagicMock


def setup_try_logging_in_mocks(check_password_hash_return_value):
    # Create Mock values
    mock = TryLoggingInMocks(
        patch_root="middleware.login_queries",
        mocks_to_patch=["login_response", "check_password_hash", "unauthorized_response"],
    )
    mock.user_info = DatabaseClient.UserInfo(
        password_digest=mock.password_digest,
        id=mock.user_id,
        api_key=None,
        email=mock.email,
    )
    mock.db_client.get_user_info = MagicMock(return_value=mock.user_info)
    mock.check_password_hash.return_value = check_password_hash_return_value

    return mock


def test_try_logging_in_successful():
    mock = setup_try_logging_in_mocks(check_password_hash_return_value=True)

    # Call function
    try_logging_in(mock.db_client, mock.email, mock.password)

    # Assert
    mock.db_client.get_user_info.assert_called_with(mock.email)
    mock.check_password_hash.assert_called_with(mock.password_digest, mock.password)
    mock.unauthorized_response.assert_not_called()
    mock.login_response.assert_called_with(mock.db_client, mock.user_info)



def test_try_logging_in_unsuccessful():
    mock = setup_try_logging_in_mocks(check_password_hash_return_value=False)

    # Call function
    try_logging_in(mock.db_client, mock.email, mock.password)

    # Assert
    mock.db_client.get_user_info.assert_called_with(mock.email)
    mock.check_password_hash.assert_called_with(mock.password_digest, mock.password)
    mock.unauthorized_response.assert_called_once()
    mock.login_response.assert_not_called()



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
    mock_db_client = MagicMock()
    data_source_by_id_wrapper(arg="SOURCE_UID_1", db_client=mock_db_client)
    mock_data_source_by_id_query.assert_called_with(
        data_source_id="SOURCE_UID_1", db_client=mock_db_client
    )
    mock_make_response.assert_called_with(
        {"agency_name": "Agency A"}, HTTPStatus.OK.value
    )


def test_data_source_by_id_wrapper_data_not_found(
    mock_data_source_by_id_query, mock_make_response
):
    mock_data_source_by_id_query.side_effect = DataSourceNotFoundError
    mock_db_client = MagicMock()
    data_source_by_id_wrapper(arg="SOURCE_UID_1", db_client=mock_db_client)
    mock_data_source_by_id_query.assert_called_with(
        data_source_id="SOURCE_UID_1", db_client=mock_db_client
    )
    mock_make_response.assert_called_with(
        {"message": "Data source not found."}, HTTPStatus.OK.value
    )
