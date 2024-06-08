from http import HTTPStatus
from unittest.mock import MagicMock
from tests.fixtures import client_with_mock_db
from tests.helper_functions import check_response_status


def test_login_post(client_with_mock_db, monkeypatch):
    mock_data = {"email": "test_email", "password": "test_password"}
    mock_request = MagicMock()
    mock_request.get_json.return_value = mock_data

    mock_response = ({"message": "Test Response"}, HTTPStatus.IM_A_TEAPOT)

    mock_try_logging_in = MagicMock(return_value=mock_response)
    monkeypatch.setattr("resources.Login.try_logging_in", mock_try_logging_in)

    response = client_with_mock_db.client.post("/login", json=mock_data)
    check_response_status(response, HTTPStatus.IM_A_TEAPOT)
    assert response.json == {"message": "Test Response"}