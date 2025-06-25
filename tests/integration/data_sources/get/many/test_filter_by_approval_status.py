from db.enums import ApprovalStatus
from tests.helper_scripts.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)
from tests.integration.test_check_database_health import wipe_database


def test_data_source_get_filter_by_approval_status(
    test_data_creator_flask: TestDataCreatorFlask, test_data_creator_db_client
):
    """
    Test that GET call to /data-sources endpoint retrieves data sources and correctly identifies specific sources by name
    """
    tdc = test_data_creator_flask
    wipe_database(tdc.db_client)
    tus = tdc.standard_user()
    test_data_creator_db_client.data_source(approval_status=ApprovalStatus.PENDING)

    response_json = tdc.request_validator.get_data_sources(
        headers=tus.api_authorization_header,
        approval_status=ApprovalStatus.PENDING,
    )
    data = response_json["data"]
    assert len(data) == 1

    response_json = tdc.request_validator.get_data_sources(
        headers=tus.api_authorization_header,
        approval_status=ApprovalStatus.APPROVED,
    )
    data = response_json["data"]
    assert len(data) == 0
