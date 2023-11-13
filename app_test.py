import pytest
import os
from app import app
from flask_restful import Api
from dotenv import load_dotenv
from middleware.initialize_psycopg2_connection import initialize_psycopg2_connection, QUICK_SEARCH_QUERY
import datetime

load_dotenv()

API_KEY = os.getenv('API_KEY')

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
        cursor.execute(QUICK_SEARCH_QUERY, (f'%{search}%', f'%{search}%', f'%{search}%', f'%{search}%', f'%{location}%', f'%{location}%', f'%{location}%', f'%{location}%', f'%{location}%', f'%{location}%', f'%{location}%', f'%{location}%'))

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

# search-tokens

# user

# archives