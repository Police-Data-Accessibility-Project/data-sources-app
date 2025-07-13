from http import HTTPStatus

from tests.helper_scripts.helper_classes.test_data_creator.flask import TestDataCreatorFlask
from tests.integration.auth.signup.helpers import signup_user


def test_signup_post_user_exists_is_verified(
    test_data_creator_flask: TestDataCreatorFlask, mocker
):
    """
    If a user tries to sign up with an email that exists and is verified
    that user should receive a special error message informing them
    that the email is already in use.
    """
    tdc = test_data_creator_flask
    tus = tdc.standard_user()

    signup_user(
        request_validator=tdc.request_validator,
        email=tus.user_info.email,
        password="test",
        mocker=mocker,
        expected_response_status=HTTPStatus.CONFLICT,
        expected_json_content={"message": "User with email already exists."},
    )
