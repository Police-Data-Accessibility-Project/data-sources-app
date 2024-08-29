from http import HTTPStatus
from unittest.mock import MagicMock

from tests.fixtures import client_with_mock_db, bypass_api_key_required
from tests.helper_scripts.common_test_functions import check_response_status


def test_put_user(client_with_mock_db, monkeypatch, bypass_api_key_required):
    mock_data = {
        "email": "test_email",
        "password": "test_password",
    }
    mock_set_user_password = MagicMock()
    monkeypatch.setattr("resources.User.set_user_password", mock_set_user_password)

    response = client_with_mock_db.client.put("/user", json=mock_data)

    check_response_status(response, HTTPStatus.OK)
    assert response.json == {"message": "Successfully updated password"}

    mock_set_user_password.assert_called()
