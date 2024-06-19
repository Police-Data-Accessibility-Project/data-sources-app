import os
from app import create_app
from tests.resources.app_test_data import (
    DATA_SOURCES_ROWS,
    AGENCIES_ROWS,
)
import datetime
import sqlite3
import pytest
from unittest.mock import patch, MagicMock

current_datetime = datetime.datetime.now()
DATETIME_STRING = current_datetime.strftime("%Y-%m-%d %H:%M:%S")


@pytest.fixture()
def test_app():
    app = create_app()
    yield app


@pytest.fixture()
def client(test_app):
    return test_app.test_client()


@pytest.fixture()
def runner(test_app):
    return test_app.test_cli_runner()


@pytest.fixture()
def test_app_with_mock(mocker, monkeypatch):
    # Patch the initialize_psycopg2_connection function so it returns a MagicMock
    monkeypatch.setattr(
        "app.initialize_psycopg2_connection", lambda: mocker.MagicMock()
    )
    yield create_app()


@pytest.fixture()
def client_with_mock(test_app_with_mock):
    # Use the app with the mocked database connection to get the test client
    return test_app_with_mock.test_client()


@pytest.fixture()
def runner_with_mock(test_app_with_mock):
    # Use the app with the mocked database connection for the test CLI runner
    return test_app_with_mock.test_cli_runner()


@pytest.fixture
def session():
    connection = sqlite3.connect("file::memory:?cache=shared", uri=True)
    db_session = connection.cursor()
    with open("do_db_ddl_clean.sql", "r") as f:
        sql_file = f.read()
        sql_queries = sql_file.split(";")
        for query in sql_queries:
            db_session.execute(query.replace("\n", ""))

    for row in DATA_SOURCES_ROWS:
        fully_clean_row = [str(r) for r in row]
        fully_clean_row_str = "'" + "', '".join(fully_clean_row) + "'"
        db_session.execute(f"insert into data_sources values ({fully_clean_row_str})")
    db_session.execute(
        "update data_sources set broken_source_url_as_of = null where broken_source_url_as_of = 'NULL'"
    )

    for row in AGENCIES_ROWS:
        clean_row = [r if r is not None else "" for r in row]
        fully_clean_row = [str(r) for r in clean_row]
        fully_clean_row_str = "'" + "', '".join(fully_clean_row) + "'"
        db_session.execute(f"insert into agencies values ({fully_clean_row_str})")

    yield connection
    connection.close()


# region Resources


def test_get_api_key(client_with_mock, mocker, test_app_with_mock):
    mock_request_data = {"email": "user@example.com", "password": "password"}
    mock_user_data = {"id": 1, "password_digest": "hashed_password"}

    # Mock login_results function to return mock_user_data
    mocker.patch("resources.ApiKey.login_results", return_value=mock_user_data)
    # Mock check_password_hash based on the valid_login parameter
    mocker.patch("resources.ApiKey.check_password_hash", return_value=True)

    with client_with_mock:
        response = client_with_mock.get("/api_key", json=mock_request_data)
        json_data = response.get_json()
        assert "api_key" in json_data
        assert response.status_code == 200


# endregion
