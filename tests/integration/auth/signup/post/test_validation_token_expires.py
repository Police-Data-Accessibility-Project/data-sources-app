from datetime import datetime, timezone, timedelta
from http import HTTPStatus

from tests.helper_scripts.common_test_data import get_test_email
from tests.helper_scripts.helper_classes.test_data_creator.flask import TestDataCreatorFlask
from tests.integration.auth.signup.constants import PATCH_ROOT
from tests.integration.auth.signup.helpers import signup_user, validate_email, resend_validation_email


def test_signup_post_validation_token_expires(
    test_data_creator_flask: TestDataCreatorFlask, mocker
):
    """
    Confirm that validation token properly expires if user does not confirm email in time
    """
    tdc = test_data_creator_flask

    patch_addr = f"{PATCH_ROOT}._get_validation_expiry"

    email = get_test_email()
    # Manipulate expiry to be in the past
    mocker.patch(
        patch_addr,
        return_value=0,
    )

    # Have user sign up using the /signup endpoint, and confirm email sent
    expired_token = signup_user(
        request_validator=tdc.request_validator,
        email=email,
        password="test",
        mocker=mocker,
    )

    # Try using token in `/auth/validate-email` and be denied
    validate_email(
        tdc.request_validator,
        token=expired_token,
        expected_response_status=HTTPStatus.UNAUTHORIZED,
        expected_json_content={
            "message": "Token is expired. Please request a new token."
        },
    )

    # Reset expiry to be in the future
    mocker.patch(
        patch_addr,
        return_value=(datetime.now(tz=timezone.utc) + timedelta(days=1)).timestamp(),
    )

    # Resend validation using the `auth/resend-validation` endpoint
    token = resend_validation_email(
        tdc.request_validator,
        email=email,
        mocker=mocker,
        expected_response_status=HTTPStatus.OK,
    )

    # Try using token in `/auth/validate-email` and be successful
    validate_email(
        tdc.request_validator,
        token=token,
    )
