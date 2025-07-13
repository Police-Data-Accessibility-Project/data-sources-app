from http import HTTPStatus

from middleware.schema_and_dto.schemas.common.common_response_schemas import MessageSchema
from tests.helper_scripts.common_test_data import get_test_email
from tests.helper_scripts.helper_classes.test_data_creator.flask import TestDataCreatorFlask
from tests.integration.auth.signup.helpers import signup_user, validate_email


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
    token = signup_user(
        request_validator=tdc.request_validator,
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
    validate_email(
        tdc.request_validator,
        token=token,
        expected_response_status=HTTPStatus.OK,
    )

    # Try logging in using the /login endpoint and be successful.
    tdc.request_validator.login(
        email=email,
        password=password,
    )
