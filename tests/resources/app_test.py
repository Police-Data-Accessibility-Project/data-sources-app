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

api_key = os.getenv("VUE_APP_PDAP_API_KEY")
HEADERS = {"Authorization": f"Bearer {api_key}"}
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
def test_app_with_mock():
    # Patch the initialize_psycopg2_connection function so it returns a MagicMock
    with patch("app.initialize_psycopg2_connection") as mock_init:
        mock_connection = MagicMock()
        mock_init.return_value = mock_connection

        app = create_app()
        # If your app stores the connection in a global or app context,
        # you can also directly assign the mock_connection there

        # Provide access to the mock within the app for assertions in tests
        app.mock_connection = mock_connection

        yield app


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
        # valid_row = {k: v for k, v in row.items() if k in all_columns}
        # clean_row = [r if r is not None else "" for r in row]
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

    # sql_query_log = f"INSERT INTO quick_search_query_logs (id, search, location, results, result_count, datetime_of_request, created_at) VALUES (1, 'test', 'test', '', 0, '{DATETIME_STRING}', '{DATETIME_STRING}')"
    # db_session.execute(sql_query_log)

    yield connection
    connection.close()


# def test_post_user(client):
#     response = client.post(
#         "/user", headers=HEADERS, json={"email": "test", "password": "test"}
#     )

#     # with initialize_psycopg2_connection() as psycopg2_connection:
#     #     cursor = psycopg2_connection.cursor()
#     #     cursor.execute(f"DELETE FROM users WHERE email = 'test'")
#     #     psycopg2_connection.commit()

#     assert response.json["data"] == "Successfully added user"

# def test_put_archives(client):
#     current_datetime = datetime.datetime.now()
#     datetime_string = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
#     response = client.put(
#         "/archives",
#         headers=HEADERS,
#         json=json.dumps(
#             {
#                 "id": "test",
#                 "last_cached": datetime_string,
#                 "broken_source_url_as_of": "",
#             }
#         ),
#     )

#     assert response.json["status"] == "success"


# def test_put_archives_brokenasof(client):
#     current_datetime = datetime.datetime.now()
#     datetime_string = current_datetime.strftime("%Y-%m-%d")
#     response = client.put(
#         "/archives",
#         headers=HEADERS,
#         json=json.dumps(
#             {
#                 "id": "test",
#                 "last_cached": datetime_string,
#                 "broken_source_url_as_of": datetime_string,
#             }
#         ),
#     )

#     assert response.json["status"] == "success"


# # agencies
# def test_agencies(client):
#     response = client.get("/agencies/1", headers=HEADERS)

#     assert len(response.json["data"]) > 0


# def test_agencies_pagination(client):
#     response1 = client.get("/agencies/1", headers=HEADERS)
#     response2 = client.get("/agencies/2", headers=HEADERS)

#     assert response1 != response2

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
        test_app_with_mock.mock_connection.cursor().execute.assert_called_once()
        test_app_with_mock.mock_connection.commit.assert_called_once()


# endregion
