from db.client.core import DatabaseClient
from db.models.implementations import LinkAgencyMetaURL
from db.models.implementations.core.agency.meta_urls.sqlalchemy import MetaURL
from endpoints.v3.source_manager.sync.meta_urls.add.request import (
    AddMetaURLsOuterRequest,
    AddMetaURLsInnerRequest,
)
from endpoints.v3.source_manager.sync.meta_urls.shared.content import (
    MetaURLSyncContentModel,
)
from endpoints.v3.source_manager.sync.shared.models.response.add import (
    SourceManagerSyncAddOuterResponse,
)
from tests.integration.v3.helpers.api_test_helper import APITestHelper


def test_source_manager_meta_urls_add(
    live_database_client: DatabaseClient,
    api_test_helper: APITestHelper,
    agency_id_1: int,
    agency_id_2: int,
    meta_url_id_1: int,
):
    response: SourceManagerSyncAddOuterResponse = (
        api_test_helper.request_validator.post_v3(
            url="/source-manager/meta-urls/add",
            json=AddMetaURLsOuterRequest(
                meta_urls=[
                    AddMetaURLsInnerRequest(
                        request_id=1,
                        content=MetaURLSyncContentModel(
                            url="https://meta-url.com", agency_ids=[agency_id_1]
                        ),
                    ),
                    AddMetaURLsInnerRequest(
                        request_id=2,
                        content=MetaURLSyncContentModel(
                            url="https://meta-url-2.com",
                            agency_ids=[agency_id_2],
                        ),
                    ),
                    # Add preexisting meta url
                    AddMetaURLsInnerRequest(
                        request_id=3,
                        content=MetaURLSyncContentModel(
                            url="https://www.example.com/agency_meta_url", agency_ids=[agency_id_1]
                        ),
                    ),
                ]
            ).model_dump(mode="json"),
            expected_model=SourceManagerSyncAddOuterResponse,
        )
    )

    assert {r.request_id for r in response.entities} == {
        1,
        2,
        3,
    }

    db_ids: list[int] = [ent.app_id for ent in response.entities]
    assert meta_url_id_1 in db_ids

    meta_urls: list[dict] = live_database_client.get_all(MetaURL)
    assert len(meta_urls) == 3

    meta_url_1: dict = meta_urls[1]
    assert meta_url_1["url"] == "https://meta-url.com"
    # assert meta_url_1["agency_id"] == agency_id_1

    meta_url_2: dict = meta_urls[2]
    assert meta_url_2["url"] == "https://meta-url-2.com"
    # assert meta_url_2["agency_id"] == agency_id_2

    links: list[dict] = live_database_client.get_all(LinkAgencyMetaURL)
    assert len(links) == 3
