from unittest.mock import patch, MagicMock
from tests.helper_functions import check_response_status

import json
from http import HTTPStatus
from tests.fixtures import client_with_mock_db, bypass_api_required


def test_get_agencies(client_with_mock_db, monkeypatch, bypass_api_required):
    mock_get_agencies = MagicMock(
        return_value=(
            {
                "id": None,
                "last_cached": None,
                "source_url": None,
                "update_frequency": None,
             },
            HTTPStatus.IM_A_TEAPOT)
    )
    monkeypatch.setattr("resources.Archives.archives_get_query", mock_get_agencies)

    response = client_with_mock_db.client.get("/archives")
    check_response_status(response, HTTPStatus.IM_A_TEAPOT)
    assert response.json == mock_get_agencies.return_value[0]


def test_put_agencies(client_with_mock_db, monkeypatch, bypass_api_required):
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
