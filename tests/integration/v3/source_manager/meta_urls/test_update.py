from db.client.core import DatabaseClient
from db.models.implementations.core.agency.meta_urls.sqlalchemy import AgencyMetaURL
from endpoints.v3.source_manager.sync.meta_urls.shared.content import MetaURLSyncContentModel
from endpoints.v3.source_manager.sync.meta_urls.update.request import (
    UpdateMetaURLsOuterRequest,
    UpdateMetaURLsInnerRequest,
)
from tests.integration.v3.helpers.api_test_helper import APITestHelper


def test_source_manager_meta_urls_update(
    api_test_helper: APITestHelper,
    meta_url_id_1: int,
    meta_url_id_2: int,
    agency_id_1: int,
    agency_id_2: int,
    live_database_client: DatabaseClient,
):
    api_test_helper.request_validator.post_v3(
        url="/source-manager/meta-urls/update",
        json=UpdateMetaURLsOuterRequest(
            meta_urls=[
                UpdateMetaURLsInnerRequest(
                    app_id=meta_url_id_1,
                    content=MetaURLSyncContentModel(
                        url="https://meta-url.com/modified",
                        agency_id=agency_id_2,
                    )
                ),
                UpdateMetaURLsInnerRequest(
                    app_id=meta_url_id_2,
                    content=MetaURLSyncContentModel(
                        url="https://meta-url-2.com/modified",
                        agency_id=agency_id_1
                    )
                ),
            ]
        ).model_dump(mode="json", exclude_unset=True),
    )

    meta_urls: list[dict] = live_database_client.get_all(AgencyMetaURL)
    assert len(meta_urls) == 2

    meta_url_1: dict = meta_urls[0]
    assert meta_url_1["url"] == "https://meta-url.com/modified"
    assert meta_url_1["agency_id"] == agency_id_2

    meta_url_2: dict = meta_urls[1]
    assert meta_url_2["url"] == "https://meta-url-2.com/modified"
    assert meta_url_2["agency_id"] == agency_id_1
