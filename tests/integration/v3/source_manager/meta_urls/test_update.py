from db.client.core import DatabaseClient
from db.enums import URLStatus
from db.models.implementations import LinkAgencyMetaURL
from db.models.implementations.core.agency.meta_urls.sqlalchemy import MetaURL
from endpoints.v3.source_manager.sync.meta_urls.shared.content import (
    MetaURLSyncContentModel,
)
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
                        agency_ids=[agency_id_2],
                        url_status=URLStatus.OK,
                        internet_archive_url="https://www.example.com/internet-archive",
                    ),
                ),
                UpdateMetaURLsInnerRequest(
                    app_id=meta_url_id_2,
                    content=MetaURLSyncContentModel(
                        url="https://meta-url-2.com/modified", agency_ids=[agency_id_1]
                    ),
                ),
            ]
        ).model_dump(mode="json", exclude_unset=True),
    )

    meta_urls: list[dict] = live_database_client.get_all(MetaURL)
    assert len(meta_urls) == 2

    meta_url_1: dict = meta_urls[0]
    assert meta_url_1["url"] == "https://meta-url.com/modified"
    assert meta_url_1["url_status"] == URLStatus.OK.value
    assert (
        meta_url_1["internet_archive_url"] == "https://www.example.com/internet-archive"
    )

    meta_url_2: dict = meta_urls[1]
    assert meta_url_2["url"] == "https://meta-url-2.com/modified"

    links: list[dict] = live_database_client.get_all(LinkAgencyMetaURL)
    assert len(links) == 2
    link_tups = [(link["agency_id"], link["meta_url_id"]) for link in links]
    assert (agency_id_2, meta_url_id_1) in link_tups
    assert (agency_id_1, meta_url_id_2) in link_tups
