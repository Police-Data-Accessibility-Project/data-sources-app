
from unittest.mock import MagicMock

from tests.fixtures import client_with_mock_db, bypass_api_required
from http import HTTPStatus


from tests.helper_functions import check_response_status


def test_put_data_source_by_id(client_with_mock_db, monkeypatch, bypass_api_required):

    monkeypatch.setattr("resources.DataSources.request", MagicMock())
    # mock_request.get_json.return_value = {"name": "Updated Data Source"}
    response = client_with_mock_db.client.put("/data-sources-by-id/test_id")
    assert response.status_code == HTTPStatus.OK.value
    assert response.json == {"message": "Data source updated successfully."}


def test_put_data_source_by_id(client_with_mock_db, monkeypatch, bypass_api_required):
    # Create
    mock_request = MagicMock()
    mock_data = MagicMock()
    mock_request.get_json.return_value = mock_data
    mock_update_data_source_result = (
        {"message": "Test Response"},
        HTTPStatus.IM_A_TEAPOT,
    )
    mock_update_data_source = MagicMock(return_value=mock_update_data_source_result)

    # Patch
    monkeypatch.setattr("resources.DataSources.request", mock_request)
    monkeypatch.setattr(
        "resources.DataSources.update_data_source_wrapper", mock_update_data_source
    )

    # Call endpoint
    response = client_with_mock_db.client.put("/data-sources-by-id/test_id")

    # Check
    check_response_status(response, HTTPStatus.IM_A_TEAPOT)
    assert response.json == {"message": "Test Response"}


def test_post_data_sources(client_with_mock_db, monkeypatch, bypass_api_required):
    mock_request = MagicMock()
    mock_data = MagicMock()
    mock_request.get_json.return_value = mock_data
    mock_add_new_data_source_result = (
        {"message": "Test Response"},
        HTTPStatus.IM_A_TEAPOT,
    )
    mock_add_new_data_source_wrapper = MagicMock(return_value=mock_add_new_data_source_result)

    # Patch
    monkeypatch.setattr("resources.DataSources.request", mock_request)
    monkeypatch.setattr(
        "resources.DataSources.add_new_data_source_wrapper", mock_add_new_data_source_wrapper
    )

    # Call endpoint
    response = client_with_mock_db.client.post("/data-sources")

    # Check
    check_response_status(response, HTTPStatus.IM_A_TEAPOT)
    assert response.json == {"message": "Test Response"}

def test_get_data_sources_map(client_with_mock_db, monkeypatch, bypass_api_required):
    mock_request = MagicMock()
    mock_data = MagicMock()
    mock_request.get_json.return_value = mock_data
    mock_get_data_sources_for_map_result = (
        {"message": "Test Response"},
        HTTPStatus.IM_A_TEAPOT,
    )
    mock_get_data_sources_for_map_wrapper = MagicMock(return_value=mock_get_data_sources_for_map_result)

    # Patch
    monkeypatch.setattr("resources.DataSources.request", mock_request)
    monkeypatch.setattr(
        "resources.DataSources.get_data_sources_for_map_wrapper", mock_get_data_sources_for_map_wrapper
    )

    # Call endpoint
    response = client_with_mock_db.client.get("/data-sources-map")

    # Check
    check_response_status(response, HTTPStatus.IM_A_TEAPOT)
    assert response.json == {"message": "Test Response"}