from unittest.mock import patch, MagicMock

import pytest

from tests.helper_functions import check_response_status

patch("middleware.security.api_required", lambda x: x).start()
from tests.fixtures import client_with_mock_db

@pytest.fixture
def mock_quick_search_query(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr("resources.QuickSearch.quick_search_query", mock)
    return mock


def test_get_quick_search_results_found(client_with_mock_db, mock_quick_search_query):
    mock_quick_search_query.return_value = {
        "count": "1",
        "data": [{"id": "test_id", "name": "test_name"}],
    }
    response = client_with_mock_db.client.get("/quick-search/test_search/test_location")
    check_response_status(response, 200)
    response_json = response.json
    assert response_json["data"]["data"] == [{'id': 'test_id', 'name': 'test_name'}]
    assert response_json["data"]["count"] == '1'
    assert response_json["message"] == "Results for search successfully retrieved"

def test_get_quick_search_results_not_found(client_with_mock_db, mock_quick_search_query):
    mock_quick_search_query.return_value = {
        "count": 0,
        "data": [],
    }
    response = client_with_mock_db.client.get("/quick-search/test_search/test_location")
    check_response_status(response, 404)
    response_json = response.json
    assert response_json["count"] == 0
    assert response_json["message"] == "No results found. Please considering requesting a new data source."
