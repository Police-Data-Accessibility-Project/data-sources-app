from http import HTTPStatus
from unittest.mock import MagicMock

import pytest

from tests.fixtures import client_with_mock_db
from tests.helper_functions import check_response_status




def test_post_refresh_session(
        client_with_mock_db,
        monkeypatch
):

    mock_request = MagicMock()
    mock_data = MagicMock()
    mock_request.get_json.return_value = mock_data
    mock_refresh_session_result = ({"message": "Test Response"}, HTTPStatus.IM_A_TEAPOT)
    mock_refresh_session = MagicMock(return_value=mock_refresh_session_result)

    # Patch
    monkeypatch.setattr("resources.RefreshSession.request", mock_request)
    monkeypatch.setattr("resources.RefreshSession.refresh_session", mock_refresh_session)

    # Call endpoint
    response = client_with_mock_db.client.post("/refresh-session")

    # Check
    check_response_status(response, HTTPStatus.IM_A_TEAPOT)
    assert response.json == {"message": "Test Response"}