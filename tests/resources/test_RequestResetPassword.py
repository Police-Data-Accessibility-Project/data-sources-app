from http import HTTPStatus
from unittest.mock import MagicMock
from tests.fixtures import client_with_mock_db
from tests.helper_functions import check_response_status


def test_post_request_reset_password(client_with_mock_db, monkeypatch):

    mock_request = MagicMock()
    mock_data = MagicMock()
    mock_request.get_json.return_value = mock_data
    mock_request_reset_password_result = (
        {"message": "Test Response"},
        HTTPStatus.IM_A_TEAPOT,
    )
    mock_request_reset_password = MagicMock(
        return_value=mock_request_reset_password_result
    )

    # Patch
    monkeypatch.setattr("resources.RequestResetPassword.request", mock_request)
    monkeypatch.setattr(
        "resources.RequestResetPassword.request_reset_password",
        mock_request_reset_password,
    )

    # Call endpoint
    response = client_with_mock_db.client.post("/request-reset-password")

    # Check
    check_response_status(response, HTTPStatus.IM_A_TEAPOT)
    assert response.json == {"message": "Test Response"}
