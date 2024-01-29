import pytest
import os
from app import app
from flask_restful import Api
from middleware.quick_search_query import (
    unaltered_search_query,
    quick_search_query,
    QUICK_SEARCH_COLUMNS,
)
from middleware.data_source_queries import (
    data_sources_query,
    data_sources_results,
    data_source_by_id_query,
    data_source_by_id_results,
    DATA_SOURCES_APPROVED_COLUMNS,
)
from middleware.user_queries import user_get_results, user_post_results
from middleware.archives_queries import (
    archives_get_results,
    archives_get_query,
    archives_put_broken_as_of_results,
    archives_put_last_cached_results,
    ARCHIVES_GET_COLUMNS,
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

api_key = os.getenv("VUE_APP_PDAP_API_KEY")
HEADERS = {"Authorization": f"Bearer {api_key}"}
current_datetime = datetime.datetime.now()
DATETIME_STRING = current_datetime.strftime("%Y-%m-%d %H:%M:%S")


@pytest.fixture()
def test_app():
    yield app


@pytest.fixture()
def client(test_app):
    return test_app.test_client()


@pytest.fixture()
def runner(test_app):
    return test_app.test_cli_runner()


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
    response = data_sources_results(conn=session)

    assert response


def test_data_sources_approved(session):
    response = data_sources_results(conn=session)

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


def test_user_get_query(session):
    curs = session.cursor()
    user_data = user_get_results(curs, "test")

    assert user_data["password_digest"]


def test_user_post_query(session):
    curs = session.cursor()
    user_post_results(curs, "unit_test", "unit_test")

    email_check = curs.execute(
        f"SELECT email FROM users WHERE email = 'unit_test'"
    ).fetchone()[0]

    assert email_check == "unit_test"


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
