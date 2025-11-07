import pytest
from fastapi import HTTPException

from db.client.core import DatabaseClient
from endpoints.v3.source_manager.sync.shared.models.request import SourceManagerDeleteRequest
from tests.integration.v3.helpers.api_test_helper import APITestHelper


def test_source_manager_agencies_delete_forbid_data_source(
    data_source_id_1: int,
    agency_id_1: int,
    agency_id_2: int,
    live_database_client: DatabaseClient,
    api_test_helper: APITestHelper,
):
    with pytest.raises(HTTPException) as exc_info:
        api_test_helper.request_validator.post_v3(
            url="/source-manager/agencies/delete",
            json=SourceManagerDeleteRequest(ids=[agency_id_1, agency_id_2]).model_dump(
                mode="json"
            ),
        )
    assert exc_info.value.status_code == 400
    assert (
        exc_info.value.detail["detail"]
        == f"Cannot delete agencies with data sources: [{{'data_source_id': {data_source_id_1}, 'agency_id': {agency_id_1}}}]"
    )
