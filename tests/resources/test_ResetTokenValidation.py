from http import HTTPStatus
from unittest.mock import MagicMock
from tests.fixtures import client_with_mock_db
from tests.helper_functions import check_response_status


def test_post_reset_token_validation(client_with_mock_db, monkeypatch):

    mock_request = MagicMock()
    mock_data = {
        "token": "test_token",
    }
    mock_request.get_json.return_value = mock_data
    mock_reset_token_validation_result = ({"message": "Test Response"}, HTTPStatus.IM_A_TEAPOT)
    mock_reset_token_validation = MagicMock(return_value=mock_reset_token_validation_result)

    # Patch
    monkeypatch.setattr("resources.ResetTokenValidation.reset_token_validation", mock_reset_token_validation)

    # Call endpoint
    response = client_with_mock_db.client.post(
        "/reset-token-validation",
        json=mock_data
    )

    # Check
    check_response_status(response, HTTPStatus.IM_A_TEAPOT)
    assert response.json == {"message": "Test Response"}