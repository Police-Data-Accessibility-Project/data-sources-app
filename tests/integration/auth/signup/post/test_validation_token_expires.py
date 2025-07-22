from datetime import datetime, timezone, timedelta
from http import HTTPStatus


def test_signup_post_validation_token_expires(helper):
    """
    Confirm that validation token properly expires if user does not confirm email in time
    """

    # Manipulate expiry to be in the past
    helper.patch_expiry(0)

    # Have user sign up using the /signup endpoint, and confirm email sent
    expired_token = helper.signup_user()

    # Try using token in `/auth/validate-email` and be denied
    helper.validate_email(
        token=expired_token,
        expected_response_status=HTTPStatus.UNAUTHORIZED,
        expected_json_content={
            "message": "Token is expired. Please request a new token."
        },
    )

    # Reset expiry to be in the future
    tomorrow = datetime.now(tz=timezone.utc) + timedelta(days=1)
    helper.patch_expiry(tomorrow.timestamp())

    # Resend validation using the `auth/resend-validation` endpoint
    token = helper.resend_validation_email()

    # Try using token in `/auth/validate-email` and be successful
    helper.validate_email(
        token=token,
    )
