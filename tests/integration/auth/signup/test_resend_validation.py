from http import HTTPStatus

from tests.integration.auth.signup.helpers import SignupTestHelper


def test_resend_validation_invalid_email(
    helper: SignupTestHelper
):
    """
    If user tries to resend validation email for an email that does not exist
    that user should receive a special error message informing them
    that the email does not exist.
    """
    expected_json_content = {
        "message": "Email provided not associated with any pending user."
    }

    helper.resend_validation_email(
        expected_response_status=HTTPStatus.BAD_REQUEST,
        expected_json_content=expected_json_content,
    )

    # Do the same with an extant user
    tus = helper.tdc.standard_user()
    helper.email = tus.user_info.email
    helper.resend_validation_email(
        expected_response_status=HTTPStatus.BAD_REQUEST,
        expected_json_content=expected_json_content,
    )
