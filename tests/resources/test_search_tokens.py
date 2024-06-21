from http import HTTPStatus
from unittest.mock import MagicMock
from tests.fixtures import client_with_mock_db
from tests.helper_functions import check_response_status


def test_get_search_tokens(client_with_mock_db, monkeypatch):

    mock_request = MagicMock()
    mock_data = {
        "endpoint": "test_endpoint",
        "arg1": "test_arg1",
        "arg2": "test_arg2",
    }
    mock_request.get_json.return_value = mock_data
    mock_insert_access_token = MagicMock()
    mock_perform_endpoint_logic_result = (
        {"message": "Test Response"},
        HTTPStatus.IM_A_TEAPOT,
    )
    mock_perform_endpoint_logic = MagicMock(
        return_value=mock_perform_endpoint_logic_result
    )

    # Patch
    monkeypatch.setattr(
        "resources.SearchTokens.insert_access_token", mock_insert_access_token
    )
    monkeypatch.setattr(
        "resources.SearchTokens.perform_endpoint_logic", mock_perform_endpoint_logic
    )

    # Call endpoint
    response = client_with_mock_db.client.get("/search-tokens", json=mock_data)

    # Check
    check_response_status(response, HTTPStatus.IM_A_TEAPOT)
    assert response.json == {"message": "Test Response"}
