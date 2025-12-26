from endpoints.v3.source_manager.data_sources.duplicate.request import SourceManagerDataSourcesDuplicateRequest
from tests.helpers.helper_classes.test_data_creator.db_client_.core import TestDataCreatorDBClient
from tests.integration.v3.helpers.api_test_helper import APITestHelper


def test_source_collector_duplicates(
    test_data_creator_db_client: TestDataCreatorDBClient,
    api_test_helper: APITestHelper,
):
    ath = api_test_helper
    tdc = test_data_creator_db_client
    extant_data_sources = []
    for i in range(50):
        data_source = tdc.data_source()
        extant_data_sources.append(data_source)

    tdc.db_client.refresh_materialized_view("DISTINCT_SOURCE_URLS")

    extant_urls = [data_source.url for data_source in extant_data_sources]
    new_urls = ["https://test.com" + str(i) for i in range(50, 100)]

    data = ath.request_validator.post_v3(
        url="/data-sources/duplicates",
        json=SourceManagerDataSourcesDuplicateRequest(
            urls=extant_urls + new_urls
        ).model_dump(mode="json")
    )
    assert len(data["results"]) == 100
    for url in new_urls:
        assert not data["results"][url]
    for url in extant_urls:
        assert data["results"][url]
