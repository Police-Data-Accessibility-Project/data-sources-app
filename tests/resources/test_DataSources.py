# The below line is required to bypass the api_required decorator,
# and must be positioned prior to other imports in order to work.
from unittest.mock import patch, MagicMock
patch("middleware.security.api_required", lambda x: x).start()
from tests.fixtures import client_with_mock_db

def test_put_data_source_by_id(
    client_with_mock_db, monkeypatch
):

    monkeypatch.setattr("resources.DataSources.request", MagicMock())
    # mock_request.get_json.return_value = {"name": "Updated Data Source"}
    response = client_with_mock_db.client.put("/data-sources-by-id/test_id")
    assert response.status_code == 200
    assert response.json == {"message": "Data source updated successfully."}
