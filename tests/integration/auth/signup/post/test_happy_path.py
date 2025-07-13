from http import HTTPStatus

from middleware.schema_and_dto.schemas.common.common_response_schemas import MessageSchema


def test_signup_post(helper):
    """
    A user should be able to sign up using the `auth/signup` endpoint
    That user should receive a validation token via email
    Which they can provide to `/auth-validate/email` to validate their email
    and enable the use of `/login`
    Attempting to call `/login` prior to validation should result in an error
    """

    # Have user sign up using the /signup endpoint, and confirm email sent
    token = helper.signup_user()

    # Try logging in using the /login endpoint and be denied because email not verified
    helper.login(
        expected_response_status=HTTPStatus.UNAUTHORIZED,
        expected_schema=MessageSchema(),
        expected_json_content={"message": "Email not verified."},
    )

    # Call `/auth/validate-email` with the token sent to the user.
    # Confirm this logs in user and returns access token, refresh token, and api key.
    helper.validate_email(
        token=token,
        expected_response_status=HTTPStatus.OK,
    )

    # Try logging in using the /login endpoint and be successful.
    helper.login()
