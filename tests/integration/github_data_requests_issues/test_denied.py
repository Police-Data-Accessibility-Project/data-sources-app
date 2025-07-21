from http import HTTPStatus

from middleware.enums import PermissionsEnum
from tests.helpers.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)
from tests.helpers.helper_functions_complex import create_test_user_setup


def test_synchronize_github_issue_denied(
    test_data_creator_flask: TestDataCreatorFlask, monkeypatch, clear_data_requests
):
    # Give a user every permission except github_sync
    tdc = test_data_creator_flask
    tus = create_test_user_setup(
        tdc.flask_client,
        permissions=[
            permission
            for permission in PermissionsEnum
            if permission != PermissionsEnum.GITHUB_SYNC
        ],
    )
    return tdc.request_validator.github_data_requests_issues_synchronize(
        headers=tus.jwt_authorization_header,
        expected_response_status=HTTPStatus.FORBIDDEN,
    )
