# The below line is required to bypass the api_required decorator,
# and must be positioned prior to other imports in order to work.
from unittest.mock import patch, MagicMock
patch("middleware.security.api_required", lambda x: x).start()
from tests.fixtures import client_with_mock_db


@patch("resources.DataSources.data_source_by_id_query")
def test_get_data_source_by_id_found(
    mock_data_source_by_id_query,
    client_with_mock_db,
):
    mock_data_source_by_id_query.return_value = {"name": "Test Data Source"}
    response = client_with_mock_db.get("/data-sources-by-id/test_id")
    assert response.json == {
        "message": "Successfully found data source",
        "data": {"name": "Test Data Source"},
    }
    assert response.status_code == 200


@patch("resources.DataSources.data_source_by_id_query")
def test_get_data_source_by_id_not_found(
    mock_data_source_by_id_query,
    client_with_mock_db,
):
    mock_data_source_by_id_query.return_value = None
    response = client_with_mock_db.get("/data-sources-by-id/test_id")
    assert response.json == {"message": "Data source not found."}
    assert response.status_code == 200

def test_put_data_source_by_id(
    client_with_mock_db, monkeypatch
):

    monkeypatch.setattr("resources.DataSources.request", MagicMock())
    # mock_request.get_json.return_value = {"name": "Updated Data Source"}
    response = client_with_mock_db.put("/data-sources-by-id/test_id")
    assert response.status_code == 200
    assert response.json == {"message": "Data source updated successfully."}
