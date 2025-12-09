from db.client.core import DatabaseClient
from db.models.implementations.core.agency.meta_urls.sqlalchemy import MetaURL
from endpoints.v3.source_manager.sync.shared.models.request.delete import (
    SourceManagerDeleteRequest,
)
from tests.integration.v3.helpers.api_test_helper import APITestHelper


def test_source_manager_meta_urls_delete(
    api_test_helper: APITestHelper,
    meta_url_id_1: int,
    meta_url_id_2: int,
    live_database_client: DatabaseClient,
):
    api_test_helper.request_validator.post_v3(
        url="/sync/meta-urls/delete",
        json=SourceManagerDeleteRequest(ids=[meta_url_id_1, meta_url_id_2]).model_dump(
            mode="json"
        ),
    )

    meta_urls: list[dict] = live_database_client.get_all(MetaURL)
    assert len(meta_urls) == 0
