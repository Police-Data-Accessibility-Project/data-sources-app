from db.enums import SortOrder
from tests.helpers.helper_classes.test_data_creator.db_client_.core import (
    TestDataCreatorDBClient,
)
from tests.helpers.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)


def test_data_sources_get(
    test_data_creator_flask: TestDataCreatorFlask,
    test_data_creator_db_client: TestDataCreatorDBClient,
):
    """
    Test that GET call to /data-sources endpoint retrieves data sources and correctly identifies specific sources by name
    """
    tdc = test_data_creator_flask
    tus = tdc.standard_user()
    for i in range(100):
        test_data_creator_db_client.data_source()
    response_json = tdc.request_validator.get_data_sources(
        headers=tus.api_authorization_header,
    )
    data = response_json["data"]
    assert len(data) == 100

    # Test sort functionality
    response_json = tdc.request_validator.get_data_sources(
        headers=tus.api_authorization_header,
        sort_by="name",
        sort_order=SortOrder.ASCENDING,
    )
    data_asc = response_json["data"]

    response_json = tdc.request_validator.get_data_sources(
        headers=tus.api_authorization_header,
        sort_by="name",
        sort_order=SortOrder.DESCENDING,
    )
    data_desc = response_json["data"]

    assert data_asc[0]["name"] < data_desc[0]["name"]

    # Test limit functionality
    response_json = tdc.request_validator.get_data_sources(
        headers=tus.api_authorization_header,
        limit=10,
    )
    data = response_json["data"]
    assert len(data) == 10
