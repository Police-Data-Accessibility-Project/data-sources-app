from http import HTTPStatus

from tests.helper_scripts.common_test_data import get_test_email
from tests.helper_scripts.helper_classes.test_data_creator.flask import TestDataCreatorFlask
from tests.integration.auth.signup.helpers import signup_user


def test_signup_post_user_exists_is_not_verified(
    test_data_creator_flask: TestDataCreatorFlask, mocker
):
    """
    If a user signs up with an email that exists but is not verified
    that user should receive a special error message reminding them to
    validate their email.
    """
    # Try signing up a user that already exists but is not verified
    tdc = test_data_creator_flask

    email = get_test_email()
    signup_user(
        request_validator=tdc.request_validator,
        email=email,
        password="test",
        mocker=mocker,
    )

    signup_user(
        request_validator=tdc.request_validator,
        email=email,
        password="new_test",
        mocker=mocker,
        expected_response_status=HTTPStatus.CONFLICT,
        expected_json_content={
            "message": "User with email has already signed up. "
            "Please validate your email or request a new validation email."
        },
    )
