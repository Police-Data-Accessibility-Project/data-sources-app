from http import HTTPStatus

from tests.helpers.constants import NOTIFICATIONS_BASE_ENDPOINT
from tests.helpers.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)
from tests.helpers.helper_classes.TestUserSetup import TestUserSetup
from tests.helpers.run_and_validate_request import run_and_validate_request


def test_notifications_permission_denied(
    test_data_creator_flask: TestDataCreatorFlask, mock_format_and_send_notifications
):
    """
    Test that for basic admins and standard users, they are not able to call the endpoint
    """
    tdc = test_data_creator_flask

    def run(tus: TestUserSetup):
        run_and_validate_request(
            flask_client=tdc.flask_client,
            http_method="post",
            endpoint=NOTIFICATIONS_BASE_ENDPOINT,
            headers=tus.jwt_authorization_header,
            expected_response_status=HTTPStatus.FORBIDDEN,
        )

    run(tdc.get_admin_tus())
    run(tdc.standard_user())
