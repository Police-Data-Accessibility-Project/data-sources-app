from db.client.core import DatabaseClient
from db.models.implementations.core.data_source.core import DataSource
from endpoints.v3.source_manager.sync.shared.models.request.delete import (
    SourceManagerDeleteRequest,
)
from tests.integration.v3.helpers.api_test_helper import APITestHelper


def test_source_manager_data_sources_delete(
    live_database_client: DatabaseClient,
    api_test_helper: APITestHelper,
    data_source_id_1: int,
    data_source_id_2: int,
):
    api_test_helper.request_validator.post_v3(
        url="/source-manager/data-sources/delete",
        json=SourceManagerDeleteRequest(
            ids=[data_source_id_1, data_source_id_2]
        ).model_dump(mode="json"),
    )

    data_sources: list[dict] = live_database_client.get_all(DataSource)
    assert len(data_sources) == 0
