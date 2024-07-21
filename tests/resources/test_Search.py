from http import HTTPStatus
from typing import Optional
from unittest.mock import MagicMock

from database_client.database_client import DatabaseClient
from tests.fixtures import client_with_mock_db, bypass_api_required
from tests.helper_functions import check_response_status
from utilities.enums import RecordCategories


def mock_search_wrapper_all_parameters(
    db_client: DatabaseClient,
    state: str,
    record_category: Optional[RecordCategories] = None,
    county: Optional[str] = None,
    locality: Optional[str] = None,
):
    assert state == "Pennsylvania"
    assert record_category == RecordCategories.POLICE
    assert county == "Allegheny"
    assert locality == "Pittsburgh"

    mock_response = ({"message": "Test Response"}, HTTPStatus.IM_A_TEAPOT)
    return mock_response

def test_search_get_all_parameters(client_with_mock_db, monkeypatch, bypass_api_required):

    monkeypatch.setattr("resources.Search.search_wrapper", mock_search_wrapper_all_parameters)

    response = client_with_mock_db.client.get(
        "/search/search-location-and-record-type?state=Pennsylvania&county=Allegheny&locality=Pittsburgh&record_category=Police%20%26%20Public%20Interactions"
    )
    check_response_status(response, HTTPStatus.IM_A_TEAPOT)
    assert response.json == {"message": "Test Response"}


def mock_search_wrapper_minimal_parameters(
    db_client: DatabaseClient,
    state: str,
    record_category: Optional[RecordCategories] = None,
    county: Optional[str] = None,
    locality: Optional[str] = None,
):
    assert state == "Pennsylvania"
    assert record_category is None
    assert county is None
    assert locality is None

    mock_response = ({"message": "Test Response"}, HTTPStatus.IM_A_TEAPOT)
    return mock_response

def test_search_get_minimal_parameters(client_with_mock_db, monkeypatch, bypass_api_required):

    monkeypatch.setattr("resources.Search.search_wrapper", mock_search_wrapper_minimal_parameters)

    response = client_with_mock_db.client.get("/search/search-location-and-record-type?state=Pennsylvania")
    check_response_status(response, HTTPStatus.IM_A_TEAPOT)
    assert response.json == {"message": "Test Response"}