from db.client.core import DatabaseClient
from db.models.implementations.core.agency.meta_urls.sqlalchemy import AgencyMetaURL
from endpoints.v3.source_manager.sync.meta_urls.add.request import (
    AddMetaURLsOuterRequest,
    AddMetaURLsInnerRequest,
)
from endpoints.v3.source_manager.sync.shared import (
    SourceManagerSyncAddOuterResponse,
)
from tests.integration.v3.helpers.api_test_helper import APITestHelper


def test_source_manager_meta_urls_add(
    live_database_client: DatabaseClient,
    api_test_helper: APITestHelper,
    agency_id_1: int,
    agency_id_2: int,
):
    response: SourceManagerSyncAddOuterResponse = (
        api_test_helper.request_validator.post_v3(
            url="/source-manager/meta-urls/add",
            json=AddMetaURLsOuterRequest(
                meta_urls=[
                    AddMetaURLsInnerRequest(
                        request_id=1, url="https://meta-url.com", agency_id=agency_id_1
                    ),
                    AddMetaURLsInnerRequest(
                        request_id=2,
                        url="https://meta-url-2.com",
                        agency_id=agency_id_2,
                    ),
                ]
            ).model_dump(mode="json"),
            expected_model=SourceManagerSyncAddOuterResponse,
        )
    )

    assert {r.request_id for r in response.entities} == {
        1,
        2,
    }

    meta_urls: list[dict] = live_database_client.get_all(AgencyMetaURL)
    assert len(meta_urls) == 2

    meta_url_1: dict = meta_urls[0]
    assert meta_url_1["url"] == "https://meta-url.com"
    assert meta_url_1["agency_id"] == agency_id_1

    meta_url_2: dict = meta_urls[1]
    assert meta_url_2["url"] == "https://meta-url-2.com"
    assert meta_url_2["agency_id"] == agency_id_2
