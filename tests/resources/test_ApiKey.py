from http import HTTPStatus
from unittest.mock import MagicMock
from tests.fixtures import client_with_mock_db
from tests.helper_functions import check_response_status

def test_get_api_key(client_with_mock_db, monkeypatch):
    mock_request = MagicMock()
    mock_data = {
        "email": "test_email",
        "password": "test_password",
    }
    mock_request.get_json.return_value = mock_data
    mock_get_api_key_result = ({"message": "Test Response"}, HTTPStatus.IM_A_TEAPOT)
    mock_get_api_key = MagicMock(return_value=mock_get_api_key_result)

    # Patch
    monkeypatch.setattr("resources.ApiKey.get_api_key_for_user", mock_get_api_key)

    # Call endpoint
    response = client_with_mock_db.client.get("/api_key", json=mock_data)

    # Check
    check_response_status(response, HTTPStatus.IM_A_TEAPOT)
    assert response.json == {"message": "Test Response"}