import pytest
import os
from app import app
from flask_restful import Api
from middleware.initialize_psycopg2_connection import initialize_psycopg2_connection, QUICK_SEARCH_QUERY
from dotenv import load_dotenv
import datetime
import json

load_dotenv()

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


# unit tests
def test_psycopg2_connection(client):
    with initialize_psycopg2_connection() as psycopg2_connection:
        assert type(psycopg2_connection) != dict


def test_data_sources_query(client):
    with initialize_psycopg2_connection() as psycopg2_connection:
        cursor = psycopg2_connection.cursor()
        search = "calls"
        location = "chicago"
        cursor.execute(QUICK_SEARCH_QUERY, (f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%", f"%{location}%", f"%{location}%", f"%{location}%", f"%{location}%", f"%{location}%", f"%{location}%", f"%{location}%", f"%{location}%"))

        assert len(cursor.fetchall()) > 0


def test_quick_search_logging(client):
    with initialize_psycopg2_connection() as psycopg2_connection:
        current_datetime = datetime.datetime.now()
        datetime_string = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

        cursor_query_log = psycopg2_connection.cursor()
        sql_query_log = "INSERT INTO quick_search_query_logs (search, location, results, result_count, datetime_of_request) VALUES (%s, %s, %s, %s, %s)"
        cursor_query_log.execute(sql_query_log, ("test", "test", [], 0, datetime_string))
        psycopg2_connection.commit()

        cursor_query_log.execute(f"SELECT * FROM quick_search_query_logs WHERE datetime_of_request = '{datetime_string}'")
        results = cursor_query_log.fetchall()

        cursor_query_log.execute(f"DELETE FROM quick_search_query_logs WHERE datetime_of_request = '{datetime_string}'")
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
        "state_iso"
    ]

    assert not set(column_names).difference(response.json["data"][0].keys()) 


def test_quicksearch_complaints_allegheny_county_results(client):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = client.get("/quick-search/complaints/allegheny county", headers=headers)

    assert len(response.json["data"]) > 0


def test_quicksearch_officer_involved_shootings_philadelphia_results(client):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = client.get("/quick-search/Officer Involved Shootings/philadelphia", headers=headers)

    assert len(response.json["data"]) > 0


def test_quicksearch_officer_involved_shootings_philadelphia_county_results(client):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = client.get("/quick-search/Officer Involved Shootings/philadelphia county", headers=headers)

    assert len(response.json["data"]) > 0


def test_quicksearch_officer_involved_shootings_kings_results(client):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = client.get("/quick-search/Officer Involved Shootings/kings", headers=headers)

    assert len(response.json["data"]) > 0


def test_quicksearch_officer_involved_shootings_kings_county_results(client):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = client.get("/quick-search/Officer Involved Shootings/kings county", headers=headers)

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
    response = client.get("/quick-search/officer involved shootings/Philadelphia", headers=headers)

    assert len(response.json["data"]) > 0
        
        
# data-sources
def test_data_source_by_id(client):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = client.get("/data-sources/reczwxaH31Wf9gRjS", headers=headers)

    assert response.json["data_source_id"] == "reczwxaH31Wf9gRjS"


def test_data_source_by_id_columns(client):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = client.get("/data-sources/reczwxaH31Wf9gRjS", headers=headers)
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
        "agency_id"
    ]

    assert not set(column_names).difference(response.json.keys()) 


def test_data_sources(client):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = client.get("/data-sources", headers=headers)

    assert len(response.json["data"]) > 0


def test_data_sources_approved(client):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = client.get("/data-sources", headers=headers)
    unapproved_url = 'https://joinstatepolice.ny.gov/15-mile-run'

    assert len([d for d in response.json["data"] if d["source_url"] == unapproved_url]) == 0


def test_data_source_by_id_approved(client):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = client.get("/data-sources/rec013MFNfBnrTpZj", headers=headers)

    assert response.json == 'Data source not found.'


# search-tokens (WIP)
# def test_search_tokens_data_sources(client):
#     headers = {"Authorization": f"Bearer {API_KEY}"}
#     response = client.get("/search-tokens/data-sources/test/test", headers=headers)

#     assert len(response.json["data"]) > 0


# def test_search_tokens_data_source_by_id(client):
#     headers = {"Authorization": f"Bearer {API_KEY}"}
#     response = client.get("/search-tokens/data-sources/reczwxaH31Wf9gRjS/test", headers=headers)

#     assert response.json["data_source_id"] == "reczwxaH31Wf9gRjS"


def test_search_tokens_quick_search_complaints_allegheny_results(client):
    response = client.get("/search-tokens/quick-search/calls/chicago")
    print(response)

    assert len(response.json["data"]) > 0


user
def test_get_user(client):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = client.get("/user", headers=headers, json={"email": "test2", "password": "test"})

    assert response

def test_post_user(client):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = client.post("/user", headers=headers, json={"email": "test", "password": "test"})

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

    column_names = ["id", "source_url", "update_frequency", "last_cached", "agency_name"]
    
    assert not set(column_names).difference(response.json[0].keys())

def test_put_archives(client):
    current_datetime = datetime.datetime.now()
    datetime_string = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = client.put("/archives", headers=headers, json=json.dumps({"id": "test", "last_cached": datetime_string, "broken_source_url_as_of": ""}))

    assert response.json["status"] == "success"


def test_put_archives_brokenasof(client):
    current_datetime = datetime.datetime.now()
    datetime_string = current_datetime.strftime("%Y-%m-%d")
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = client.put("/archives", headers=headers, json=json.dumps({"id": "test", "last_cached": datetime_string, "broken_source_url_as_of": datetime_string}))

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