from tests.helper_scripts.helper_classes.TestDataCreatorFlask import (
    TestDataCreatorFlask,
)
from conftest import test_data_creator_flask, monkeysession


def test_metrics(test_data_creator_flask: TestDataCreatorFlask):

    tdc = test_data_creator_flask
    metrics = tdc.request_validator.get_metrics(
        headers=tdc.get_admin_tus().jwt_authorization_header
    )

    assert metrics["source_count"] > 0
    assert metrics["agency_count"] > 0
    assert metrics["county_count"] > 0
    assert metrics["state_count"] > 0
