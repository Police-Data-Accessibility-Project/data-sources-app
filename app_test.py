import pytest
from app import app
from decouple import config

API_KEY = config('API_KEY')

@pytest.fixture()
def test_app():

    yield app


@pytest.fixture()
def client(test_app):

    return test_app.test_client()


@pytest.fixture()
def runner(test_app):
    return test_app.test_cli_runner()


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