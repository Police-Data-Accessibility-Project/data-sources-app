from http import HTTPStatus
from unittest.mock import MagicMock
from tests.fixtures import client_with_mock_db
from tests.helper_functions import check_response_status


def test_post_reset_password(client_with_mock_db, monkeypatch):

    mock_request = MagicMock()
    mock_data = {
        "token": "test_token",
        "password": "test_password",
    }
    mock_request.get_json.return_value = mock_data
    mock_reset_password_result = ({"message": "Test Response"}, HTTPStatus.IM_A_TEAPOT)
    mock_reset_password = MagicMock(return_value=mock_reset_password_result)

    # Patch
    monkeypatch.setattr("resources.ResetPassword.reset_password", mock_reset_password)

    # Call endpoint
    response = client_with_mock_db.client.post("/reset-password", json=mock_data)

    # Check
    check_response_status(response, HTTPStatus.IM_A_TEAPOT)
    assert response.json == {"message": "Test Response"}
