# The below line is required to bypass the api_required decorator,
# and must be positioned prior to other imports in order to work.
from unittest.mock import patch, MagicMock
patch("middleware.security.api_required", lambda x: x).start()
from tests.fixtures import client_with_mock_db
from http import HTTPStatus

from flask import Response

from tests.helper_functions import check_response_status


def test_put_data_source_by_id(
    client_with_mock_db, monkeypatch
):

    monkeypatch.setattr("resources.DataSources.request", MagicMock())
    # mock_request.get_json.return_value = {"name": "Updated Data Source"}
    response = client_with_mock_db.client.put("/data-sources-by-id/test_id")
    assert response.status_code == 200
    assert response.json == {"message": "Data source updated successfully."}

def test_put_data_source_by_id(
    client_with_mock_db, monkeypatch
):

    # Create
    mock_request = MagicMock()
    mock_data = MagicMock()
    mock_request.get_json.return_value = mock_data
    mock_update_data_source_result = ({"message": "Test Response"}, HTTPStatus.IM_A_TEAPOT)
    mock_update_data_source = MagicMock(return_value=mock_update_data_source_result)

    # Patch
    monkeypatch.setattr("resources.DataSources.request", mock_request)
    monkeypatch.setattr("resources.DataSources.update_data_source", mock_update_data_source)

    # Call endpoint
    response = client_with_mock_db.client.put("/data-sources-by-id/test_id")

    # Check
    check_response_status(response, HTTPStatus.IM_A_TEAPOT)
    assert response.json == {"message": "Test Response"}

def test_post_data_sources(
    client_with_mock_db, monkeypatch
):
    mock_request = MagicMock()
    mock_data = MagicMock()
    mock_request.get_json.return_value = mock_data
    mock_add_new_data_source_result = ({"message": "Test Response"}, HTTPStatus.IM_A_TEAPOT)
    mock_add_new_data_source = MagicMock(return_value=mock_add_new_data_source_result)

    # Patch
    monkeypatch.setattr("resources.DataSources.request", mock_request)
    monkeypatch.setattr("resources.DataSources.add_new_data_source", mock_add_new_data_source)

    # Call endpoint
    response = client_with_mock_db.client.post("/data-sources")

    # Check
    check_response_status(response, HTTPStatus.IM_A_TEAPOT)
    assert response.json == {"message": "Test Response"}
