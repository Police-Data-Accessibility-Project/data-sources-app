import pytest
import os
from app import create_app
from flask_restful import Api
from middleware.quick_search_query import (
    unaltered_search_query,
    quick_search_query,
    QUICK_SEARCH_COLUMNS,
)
from middleware.data_source_queries import (
    data_sources_query,
    needs_identification_data_sources,
    data_source_by_id_query,
    data_source_by_id_results,
    DATA_SOURCES_APPROVED_COLUMNS,
    get_approved_data_sources,
    get_data_sources_for_map,
)
from middleware.user_queries import (
    user_post_results,
    user_check_email,
)
from middleware.login_queries import (
    login_results,
    create_session_token,
    token_results,
    is_admin,
)
from middleware.archives_queries import (
    archives_get_results,
    archives_get_query,
    archives_put_broken_as_of_results,
    archives_put_last_cached_results,
    ARCHIVES_GET_COLUMNS,
)
from middleware.reset_token_queries import (
    check_reset_token,
    add_reset_token,
    delete_reset_token,
)
from app_test_data import (
    DATA_SOURCES_ROWS,
    DATA_SOURCE_QUERY_RESULTS,
    QUICK_SEARCH_QUERY_RESULTS,
    AGENCIES_ROWS,
    DATA_SOURCES_ID_QUERY_RESULTS,
    ARCHIVES_GET_QUERY_RESULTS,
)
import datetime
import sqlite3
import pytest
from resources.ApiKey import (
    ApiKey,
)  # Adjust the import according to your project structure
from werkzeug.security import check_password_hash
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


# unit tests
def test_unaltered_search_query(session):
    response = unaltered_search_query(session.cursor(), "calls", "chicago")

    assert response


def test_data_sources(session):
    response = get_approved_data_sources(conn=session)

    assert response


def test_needs_identification(session):
    response = needs_identification_data_sources(conn=session)

    assert response


def test_data_sources_approved(session):
    response = get_approved_data_sources(conn=session)

    assert (
        len([d for d in response if "https://joinstatepolice.ny.gov/15-mile-run" in d])
        == 0
    )


def test_data_source_by_id_results(session):
    response = data_source_by_id_results(
        data_source_id="rec00T2YLS2jU7Tbn", conn=session
    )

    assert response


def test_data_source_by_id_approved(session):
    response = data_source_by_id_results(
        data_source_id="rec013MFNfBnrTpZj", conn=session
    )

    assert not response


def test_data_sources(session):
    response = get_data_sources_for_map(conn=session)

    assert response


def test_user_post_query(session):
    curs = session.cursor()
    user_post_results(curs, "unit_test", "unit_test")

    email_check = curs.execute(
        f"SELECT email FROM users WHERE email = 'unit_test'"
    ).fetchone()[0]

    assert email_check == "unit_test"


def test_login_query(session):
    curs = session.cursor()
    user_data = login_results(curs, "test")

    assert user_data["password_digest"]


def test_create_session_token_results(session):
    curs = session.cursor()
    token = create_session_token(curs, 1, "test")

    curs = session.cursor()
    new_token = token_results(curs, token)

    assert new_token["email"]


def test_is_admin(session):
    curs = session.cursor()
    admin = is_admin(curs, "mbodenator@gmail.com")

    assert admin


def test_not_admin(session):
    curs = session.cursor()
    admin = is_admin(curs, "test")

    assert not admin


def test_user_check_email(session):
    curs = session.cursor()
    user_data = user_check_email(curs, "test")
    print(user_data)

    assert user_data["id"]


def test_check_reset_token(session):
    curs = session.cursor()
    reset_token = check_reset_token(curs, "test")
    print(reset_token)

    assert reset_token["id"]


def test_add_reset_token(session):
    curs = session.cursor()
    add_reset_token(curs, "unit_test", "unit_test")

    email_check = curs.execute(
        f"SELECT email FROM reset_tokens WHERE email = 'unit_test'"
    ).fetchone()[0]

    assert email_check == "unit_test"


def test_delete_reset_token(session):
    curs = session.cursor()
    delete_reset_token(curs, "test", "test")

    email_check = curs.execute(
        f"SELECT email FROM reset_tokens WHERE email = 'test'"
    ).fetchone()

    assert not email_check


def test_archives_get_results(session):
    response = archives_get_results(conn=session)

    assert response


def test_archives_put_broken_as_of(session):
    archives_put_broken_as_of_results(
        id="rec00T2YLS2jU7Tbn",
        broken_as_of=DATETIME_STRING,
        last_cached=DATETIME_STRING,
        conn=session,
    )
    curs = session.cursor()
    broken_check, last_check = curs.execute(
        f"SELECT broken_source_url_as_of, last_cached FROM data_sources WHERE airtable_uid = 'rec00T2YLS2jU7Tbn'"
    ).fetchone()

    assert broken_check == DATETIME_STRING
    assert last_check == DATETIME_STRING


def test_archives_put_last_cached(session):
    archives_put_last_cached_results(
        id="recUGIoPQbJ6laBmr", last_cached=DATETIME_STRING, conn=session
    )
    curs = session.cursor()
    last_check = curs.execute(
        f"SELECT last_cached FROM data_sources WHERE airtable_uid = 'recUGIoPQbJ6laBmr'"
    ).fetchone()[0]

    assert last_check == DATETIME_STRING


# quick-search
def test_quicksearch_columns():
    response = quick_search_query(
        search="", location="", test_query_results=QUICK_SEARCH_QUERY_RESULTS
    )

    assert not set(QUICK_SEARCH_COLUMNS).difference(response["data"][0].keys())
    assert type(response["data"][1]["record_format"]) == list


# data-sources
def test_data_sources_columns():
    response = data_sources_query(conn={}, test_query_results=DATA_SOURCE_QUERY_RESULTS)

    assert not set(DATA_SOURCES_APPROVED_COLUMNS).difference(response[0].keys())


def test_data_source_by_id_columns():
    response = data_source_by_id_query("", DATA_SOURCES_ID_QUERY_RESULTS, {})

    assert not set(DATA_SOURCES_APPROVED_COLUMNS).difference(response.keys())


# user


# def test_post_user(client):
#     response = client.post(
#         "/user", headers=HEADERS, json={"email": "test", "password": "test"}
#     )

#     # with initialize_psycopg2_connection() as psycopg2_connection:
#     #     cursor = psycopg2_connection.cursor()
#     #     cursor.execute(f"DELETE FROM users WHERE email = 'test'")
#     #     psycopg2_connection.commit()

#     assert response.json["data"] == "Successfully added user"


# archives
def test_archives_get_columns():
    response = archives_get_query(
        test_query_results=ARCHIVES_GET_QUERY_RESULTS, conn={}
    )

    assert not set(ARCHIVES_GET_COLUMNS).difference(response[0].keys())


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
