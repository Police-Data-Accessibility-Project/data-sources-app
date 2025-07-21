"""Integration tests for /data-sources endpoint"""

from http import HTTPStatus

from tests.helpers.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)
from tests.helpers.run_and_validate_request import run_and_validate_request


def test_data_sources_reject_wrong_authorization(
    test_data_creator_flask: TestDataCreatorFlask,
):
    tdc = test_data_creator_flask

    data_source = tdc.data_source()

    run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="post",
        endpoint=f"/api/data-sources/{data_source.id}/reject",
        headers=tdc.standard_user().jwt_authorization_header,
        expected_response_status=HTTPStatus.FORBIDDEN,
    )
