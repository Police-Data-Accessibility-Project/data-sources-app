from tests.fixtures import client_with_mock_db
from unittest.mock import patch, MagicMock
from tests.helper_functions import check_response_status

import json
from http import HTTPStatus

def test_get_callback(client_with_mock_db, monkeypatch):
    mock_callback_outer_wrapper = MagicMock(
        return_value=({"message": "Test Response"}, HTTPStatus.IM_A_TEAPOT)
    )
    monkeypatch.setattr("resources.Callback.callback_outer_wrapper", mock_callback_outer_wrapper)
    response = client_with_mock_db.client.get("auth/callback")
    check_response_status(response, HTTPStatus.IM_A_TEAPOT)
