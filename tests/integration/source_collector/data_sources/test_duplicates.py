from tests.helper_scripts.helper_classes.TestDataCreatorFlask import (
    TestDataCreatorFlask,
)


def test_source_collector_duplicates(test_data_creator_flask: TestDataCreatorFlask):
    tdc = test_data_creator_flask
    extant_data_sources = []
    for i in range(50):
        data_source = tdc.data_source()
        extant_data_sources.append(data_source)

    tdc.db_client.refresh_materialized_view("DISTINCT_SOURCE_URLS")

    extant_urls = [data_source.url for data_source in extant_data_sources]
    new_urls = ["https://test.com" + str(i) for i in range(50, 100)]

    data = tdc.request_validator.post_source_collector_duplicates(
        headers=tdc.get_admin_tus().jwt_authorization_header,
        urls=extant_urls + new_urls,
    )
    assert len(data["results"]) == 100
    for url in new_urls:
        assert data["results"][url] == False
    for url in extant_urls:
        assert data["results"][url] == True
