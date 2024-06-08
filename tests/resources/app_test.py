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
def test_app_with_mock(mocker):
    # Patch the initialize_psycopg2_connection function so it returns a MagicMock
    yield create_app(mocker.MagicMock())


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

