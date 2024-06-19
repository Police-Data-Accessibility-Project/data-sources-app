# The below line is required to bypass the api_required decorator,
# and must be positioned prior to other imports in order to work.
from unittest.mock import patch, MagicMock

from tests.helper_functions import check_response_status

patch("middleware.security.api_required", lambda x: x).start()
import datetime
import json
import uuid
from http import HTTPStatus
from tests.fixtures import client_with_mock_db


def test_put_agencies(client_with_mock_db, monkeypatch):
    mock_data = {
        "id": "test_id",
        "last_cached": "2019-01-01",
        "broken_source_url_as_of": "2019-02-02",
    }
    mock_request = MagicMock()
    mock_request.get_json = MagicMock(return_value=json.dumps(mock_data))
    monkeypatch.setattr("resources.Archives.request", mock_request)
    mock_update_archives_data = MagicMock(
        return_value=({"message": "Test Response"}, HTTPStatus.IM_A_TEAPOT)
    )
    monkeypatch.setattr(
        "resources.Archives.update_archives_data", mock_update_archives_data
    )

    response = client_with_mock_db.client.put("/archives")
    check_response_status(response, HTTPStatus.IM_A_TEAPOT)
    assert response.json == {"message": "Test Response"}
