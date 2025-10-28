from db.client.core import DatabaseClient
from db.models.implementations.core.agency.core import Agency
from endpoints.v3.sync.shared.models.request.delete import SourceManagerDeleteRequest
from tests.integration.v3.helpers.api_test_helper import APITestHelper


def test_source_manager_agencies_delete_happy_path(
    agency_id_1: int,
    agency_id_2: int,
    live_database_client: DatabaseClient,
    api_test_helper: APITestHelper,
):
    api_test_helper.request_validator.post_v3(
        url="/source-manager/agencies/delete",
        json=SourceManagerDeleteRequest(ids=[agency_id_1, agency_id_2]).model_dump(
            mode="json"
        ),
    )

    agencies: list[dict] = live_database_client.get_all(Agency)
    assert len(agencies) == 0
