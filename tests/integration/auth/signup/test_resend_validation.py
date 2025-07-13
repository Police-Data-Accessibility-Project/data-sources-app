from http import HTTPStatus

from tests.helper_scripts.common_test_data import get_test_email
from tests.helper_scripts.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)
from tests.integration.auth.signup.helpers import resend_validation_email


def test_resend_validation_invalid_email(
    test_data_creator_flask: TestDataCreatorFlask, mocker
):
    """
    If user tries to resend validation email for an email that does not exist
    that user should receive a special error message informing them
    that the email does not exist.
    """
    tdc = test_data_creator_flask
    expected_json_content = {
        "message": "Email provided not associated with any pending user."
    }

    email = get_test_email()
    resend_validation_email(
        tdc.request_validator,
        email=email,
        mocker=mocker,
        expected_response_status=HTTPStatus.BAD_REQUEST,
        expected_json_content=expected_json_content,
    )

    # Do the same with an extant user
    tus = tdc.standard_user()
    resend_validation_email(
        tdc.request_validator,
        email=tus.user_info.email,
        mocker=mocker,
        expected_response_status=HTTPStatus.BAD_REQUEST,
        expected_json_content=expected_json_content,
    )
