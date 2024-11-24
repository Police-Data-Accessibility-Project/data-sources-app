from datetime import datetime, timezone, timedelta
from http import HTTPStatus

import pytest

from conftest import test_data_creator_flask, monkeysession
from middleware.schema_and_dto_logic.common_response_schemas import MessageSchema
from tests.helper_scripts.common_test_data import get_test_email
from tests.helper_scripts.helper_classes.TestDataCreatorFlask import (
    TestDataCreatorFlask,
)


def test_signup_post(test_data_creator_flask: TestDataCreatorFlask, mocker):
    """
    A user should be able to sign up using the `auth/signup` endpoint
    That user should receive a validation token via email
    Which they can provide to `/auth-validate/email` to validate their email
    and enable the use of `/login`
    Attempting to call `/login` prior to validation should result in an error
    """
    tdc = test_data_creator_flask

    email = get_test_email()
    password = "test_password"

    # Have user sign up using the /signup endpoint, and confirm email sent
    token = tdc.request_validator.signup(
        email=email,
        password=password,
        mocker=mocker,
    )

    # Try logging in using the /login endpoint and be denied because email not verified
    tdc.request_validator.login(
        email=email,
        password=password,
        expected_response_status=HTTPStatus.UNAUTHORIZED,
        expected_schema=MessageSchema(),
        expected_json_content={"message": "Email not verified."},
    )

    # Call `/auth/validate-email` with the token sent to the user.
    # Confirm this logs in user and returns access token, refresh token, and api key.
    tdc.request_validator.validate_email(
        token=token,
        expected_response_status=HTTPStatus.OK,
    )

    # Try logging in using the /login endpoint and be successful.
    tdc.request_validator.login(
        email=email,
        password=password,
    )


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

    tdc.request_validator.signup(
        email=tus.user_info.email,
        password="test",
        mocker=mocker,
        expected_response_status=HTTPStatus.CONFLICT,
        expected_json_content={"message": "User with email already exists."},
    )


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
    tdc.request_validator.signup(
        email=email,
        password="test",
        mocker=mocker,
    )

    tdc.request_validator.signup(
        email=email,
        password="new_test",
        mocker=mocker,
        expected_response_status=HTTPStatus.CONFLICT,
        expected_json_content={
            "message": f"User with email has already signed up. "
            f"Please validate your email or request a new validation email."
        },
    )


def test_signup_post_validation_token_expires(
    test_data_creator_flask: TestDataCreatorFlask, mocker
):
    """
    Confirm that validation token properly expires if user does not confirm email in time
    """
    tdc = test_data_creator_flask

    email = get_test_email()
    # Manipulate expiry to be in the past
    mocker.patch(
        "middleware.primary_resource_logic.signup_logic.get_validation_expiry",
        return_value=0,
    )

    # Have user sign up using the /signup endpoint, and confirm email sent
    expired_token = tdc.request_validator.signup(
        email=email,
        password="test",
        mocker=mocker,
    )

    # Try using token in `/auth/validate-email` and be denied
    tdc.request_validator.validate_email(
        token=expired_token,
        expected_response_status=HTTPStatus.UNAUTHORIZED,
        expected_json_content={
            "message": "Token is expired. Please request a new token."
        },
    )

    # Reset expiry to be in the future
    mocker.patch(
        "middleware.primary_resource_logic.signup_logic.get_validation_expiry",
        return_value=(datetime.now(tz=timezone.utc) + timedelta(days=1)).timestamp(),
    )

    # Resend validation using the `auth/resend-validation` endpoint
    token = tdc.request_validator.resend_validation_email(
        email=email,
        mocker=mocker,
        expected_response_status=HTTPStatus.OK,
    )

    # Try using token in `/auth/validate-email` and be successful
    tdc.request_validator.validate_email(
        token=token,
    )


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
    tdc.request_validator.resend_validation_email(
        email=email,
        mocker=mocker,
        expected_response_status=HTTPStatus.BAD_REQUEST,
        expected_json_content=expected_json_content,
    )

    # Do the same with an extant user
    tus = tdc.standard_user()
    tdc.request_validator.resend_validation_email(
        email=tus.user_info.email,
        mocker=mocker,
        expected_response_status=HTTPStatus.BAD_REQUEST,
        expected_json_content=expected_json_content,
    )
