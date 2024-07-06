from http import HTTPStatus
from unittest.mock import MagicMock

from tests.fixtures import client_with_mock_db, bypass_api_required
from tests.helper_functions import check_response_status

def test_get_typeahead_suggestions(client_with_mock_db, monkeypatch, bypass_api_required):
    mock_data = {"query": "test_query"}
    mock_request = MagicMock()
    mock_request.get_json.return_value = mock_data

    mock_response = ({"message": "Test Response"}, HTTPStatus.IM_A_TEAPOT)

    mock_get_typeahead_suggestions = MagicMock(return_value=mock_response)
    monkeypatch.setattr("resources.TypeaheadSuggestions.get_typeahead_suggestions_wrapper", mock_get_typeahead_suggestions)

    response = client_with_mock_db.client.get("/typeahead-suggestions", json=mock_data)

    check_response_status(response, HTTPStatus.IM_A_TEAPOT)
    assert response.json == {"message": "Test Response"}