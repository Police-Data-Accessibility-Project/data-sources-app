import pytest
import os
from app import app
from flask_restful import Api
from middleware.initialize_psycopg2_connection import initialize_psycopg2_connection
from middleware.quick_search_query import QUICK_SEARCH_SQL
import datetime
import json

API_KEY = os.getenv("VUE_APP_PDAP_API_KEY")


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
        cur.execute(query.replace("\n", ""))

    rows = [{'airtable_uid': 'rec00T2YLS2jU7Tbn', 'data_source_name': 'Calls for Service for Chicago Police Department - IL', 'description': None, 'record_type': 'Calls for Service', 'source_url': 'https://informationportal.igchicago.org/911-calls-for-cpd-service/', 'record_format': None, 'coverage_start': '2019-01-01', 'coverage_end': None, 'agency_supplied': True, 'agency_name': 'Chicago Police Department - IL', 'municipality': 'Chicago', 'state_iso': 'IL'}, {'airtable_uid': 'recUGIoPQbJ6laBmr', 'data_source_name': '311 Calls for City of Chicago', 'description': '311 Service Requests received by the City of Chicago. This dataset includes requests created after the launch of the new 311 system on 12/18/2018 and some records from the previous system, indicated in the LEGACY\\_RECORD column.\n\nIncluded as a Data Source because in some cities 311 calls lead to police response; that does not appear to be the case in Chicago.\n', 'record_type': 'Calls for Service', 'source_url': 'https://data.cityofchicago.org/Service-Requests/311-Service-Requests/v6vf-nfxy', 'record_format': ['CSV', 'XML', 'RDF', 'RSS'], 'coverage_start': '2018-12-18', 'coverage_end': None, 'agency_supplied': False, 'agency_name': 'Chicago Police Department - IL', 'municipality': 'Chicago', 'state_iso': 'IL'}]
    clean_row = [r if r is not None else "" for r in rows[0].values()]
    fully_clean_row = [r if r is not True else 'True' for r in clean_row]
    fully_clean_row_str = "'" + "', '".join(fully_clean_row) + "'"
    col_str = ", ".join(rows[0].keys())
    cur.execute(f"insert into data_sources ({col_str}) values ({fully_clean_row_str})")
    # sqlite3.OperationalError: table data_sources has no column named data_source_name

    yield db_session
    connection.close()


@pytest.fixture
def setup_db(session):

# unit tests
def test_psycopg2_connection(client):
    with initialize_psycopg2_connection() as psycopg2_connection:
        assert type(psycopg2_connection) != dict


def test_data_sources_query(client):
    with initialize_psycopg2_connection() as psycopg2_connection:
        cursor = psycopg2_connection.cursor()
        search = "calls"
        location = "chicago"
        cursor.execute(
            QUICK_SEARCH_SQL,
            (
                f"%{search}%",
                f"%{search}%",
                f"%{search}%",
                f"%{search}%",
                f"%{location}%",
                f"%{location}%",
                f"%{location}%",
                f"%{location}%",
                f"%{location}%",
                f"%{location}%",
                f"%{location}%",
                f"%{location}%",
            ),
        )

        assert len(cursor.fetchall()) > 0


def test_quick_search_logging(client):
    with initialize_psycopg2_connection() as psycopg2_connection:
        current_datetime = datetime.datetime.now()
        datetime_string = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

        cursor_query_log = psycopg2_connection.cursor()
        sql_query_log = "INSERT INTO quick_search_query_logs (search, location, results, result_count, datetime_of_request) VALUES (%s, %s, %s, %s, %s)"
        cursor_query_log.execute(
            sql_query_log, ("test", "test", [], 0, datetime_string)
        )
        psycopg2_connection.commit()

        cursor_query_log.execute(
            f"SELECT * FROM quick_search_query_logs WHERE datetime_of_request = '{datetime_string}'"
        )
        results = cursor_query_log.fetchall()

        cursor_query_log.execute(
            f"DELETE FROM quick_search_query_logs WHERE datetime_of_request = '{datetime_string}'"
        )
        psycopg2_connection.commit()

    assert len(results) > 0


# quick-search
def test_quicksearch_complaints_allegheny_results(client):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = client.get("/quick-search/complaints/allegheny", headers=headers)

    assert len(response.json["data"]) > 0


def test_quicksearch_columns(client):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = client.get("/quick-search/complaints/allegheny", headers=headers)
    column_names = [
        "airtable_uid",
        "data_source_name",
        "record_type",
        "source_url",
        "record_format",
        "coverage_start",
        "coverage_end",
        "agency_name",
        "municipality",
        "state_iso",
    ]

    assert not set(column_names).difference(response.json["data"][0].keys())


def test_quicksearch_complaints_allegheny_county_results(client):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = client.get("/quick-search/complaints/allegheny county", headers=headers)

    assert len(response.json["data"]) > 0


def test_quicksearch_officer_involved_shootings_philadelphia_results(client):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = client.get(
        "/quick-search/Officer Involved Shootings/philadelphia", headers=headers
    )

    assert len(response.json["data"]) > 0


def test_quicksearch_officer_involved_shootings_philadelphia_county_results(client):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = client.get(
        "/quick-search/Officer Involved Shootings/philadelphia county", headers=headers
    )

    assert len(response.json["data"]) > 0


def test_quicksearch_officer_involved_shootings_kings_results(client):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = client.get(
        "/quick-search/Officer Involved Shootings/kings", headers=headers
    )

    assert len(response.json["data"]) > 0


def test_quicksearch_officer_involved_shootings_kings_county_results(client):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = client.get(
        "/quick-search/Officer Involved Shootings/kings county", headers=headers
    )

    assert len(response.json["data"]) > 0


def test_quicksearch_all_allgeheny_results(client):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = client.get("/quick-search/all/allegheny", headers=headers)

    assert len(response.json["data"]) > 0


def test_quicksearch_complaints_all_results(client):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = client.get("/quick-search/complaints/all", headers=headers)

    assert len(response.json["data"]) > 0


def test_quicksearch_media_bulletin_pennsylvania_results(client):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = client.get("/quick-search/media bulletin/pennsylvania", headers=headers)

    assert len(response.json["data"]) > 0


def test_quicksearch_officer_involved_shootings_philadelphia_results(client):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = client.get(
        "/quick-search/officer involved shootings/Philadelphia", headers=headers
    )

    assert len(response.json["data"]) > 0


def test_quicksearch_format_available_formatting(client):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = client.get("/quick-search/reviews/allegheny", headers=headers)

    assert type(response.json["data"][0]["record_format"]) == list


# data-sources
def test_data_source_by_id(client):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = client.get("/data-sources-by-id/reczwxaH31Wf9gRjS", headers=headers)

    assert response.json["data_source_id"] == "reczwxaH31Wf9gRjS"


def test_data_source_by_id_columns(client):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = client.get("/data-sources-by-id/reczwxaH31Wf9gRjS", headers=headers)
    column_names = [
        "description",
        "record_type",
        "agency_name",
        "state_iso",
        "county_name",
        "municipality",
        "agency_type",
        "jurisdiction_type",
        "source_url",
        "readme_url",
        "access_type",
        "record_format",
        "detail_level",
        "size",
        "access_type",
        "access_notes",
        "records_not_online",
        "agency_supplied",
        "supplying_entity",
        "agency_originated",
        "originating_entity",
        "coverage_start",
        "coverage_end",
        "source_last_updated",
        "update_frequency",
        "update_method",
        "retention_schedule",
        "number_of_records_available",
        "scraper_url",
        "data_source_created",
        "data_source_id",
        "agency_id",
    ]

    assert not set(column_names).difference(response.json.keys())


def test_data_sources(client):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = client.get("/data-sources", headers=headers)

    assert len(response.json["data"]) > 0


def test_data_sources_approved(client):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = client.get("/data-sources", headers=headers)
    unapproved_url = "https://joinstatepolice.ny.gov/15-mile-run"

    assert (
        len([d for d in response.json["data"] if d["source_url"] == unapproved_url])
        == 0
    )


def test_data_source_by_id_approved(client):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = client.get("/data-sources-by-id/rec013MFNfBnrTpZj", headers=headers)

    assert response.json == "Data source not found."


# search-tokens
def test_search_tokens_data_sources(client):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = client.get("/search-tokens?endpoint=data-sources", headers=headers)

    assert len(response.json["data"]) > 0


def test_search_tokens_data_source_by_id(client):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = client.get(
        "/search-tokens?endpoint=data-sources-by-id&arg1=reczwxaH31Wf9gRjS",
        headers=headers,
    )

    assert response.json["data_source_id"] == "reczwxaH31Wf9gRjS"


def test_search_tokens_quick_search_complaints_allegheny_results(client):
    response = client.get(
        "/search-tokens?endpoint=quick-search&arg1=calls&arg2=chicago"
    )

    assert len(response.json["data"]) > 0


# user
def test_get_user(client):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = client.get(
        "/user", headers=headers, json={"email": "test2", "password": "test"}
    )

    assert response


def test_post_user(client):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = client.post(
        "/user", headers=headers, json={"email": "test", "password": "test"}
    )

    with initialize_psycopg2_connection() as psycopg2_connection:
        cursor = psycopg2_connection.cursor()
        cursor.execute(f"DELETE FROM users WHERE email = 'test'")
        psycopg2_connection.commit()

    assert response.json["data"] == "Successfully added user"


# archives
def test_get_archives(client):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = client.get("/archives", headers=headers)

    assert len(response.json[0]) > 0


def test_get_archives_columns(client):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = client.get("/archives", headers=headers)

    column_names = [
        "id",
        "source_url",
        "update_frequency",
        "last_cached",
        "agency_name",
    ]

    assert not set(column_names).difference(response.json[0].keys())


def test_put_archives(client):
    current_datetime = datetime.datetime.now()
    datetime_string = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = client.put(
        "/archives",
        headers=headers,
        json=json.dumps(
            {
                "id": "test",
                "last_cached": datetime_string,
                "broken_source_url_as_of": "",
            }
        ),
    )

    assert response.json["status"] == "success"


def test_put_archives_brokenasof(client):
    current_datetime = datetime.datetime.now()
    datetime_string = current_datetime.strftime("%Y-%m-%d")
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = client.put(
        "/archives",
        headers=headers,
        json=json.dumps(
            {
                "id": "test",
                "last_cached": datetime_string,
                "broken_source_url_as_of": datetime_string,
            }
        ),
    )

    assert response.json["status"] == "success"


# agencies
def test_agencies(client):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = client.get("/agencies/1", headers=headers)

    assert len(response.json["data"]) > 0


def test_agencies_pagination(client):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response1 = client.get("/agencies/1", headers=headers)
    response2 = client.get("/agencies/2", headers=headers)

    assert response1 != response2
