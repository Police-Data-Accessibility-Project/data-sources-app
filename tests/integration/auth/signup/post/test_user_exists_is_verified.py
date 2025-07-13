from http import HTTPStatus


def test_signup_post_user_exists_is_verified(
    helper
):
    """
    If a user tries to sign up with an email that exists and is verified
    that user should receive a special error message informing them
    that the email is already in use.
    """
    tus = helper.tdc.standard_user()
    helper.email = tus.user_info.email

    helper.signup_user(
        expected_response_status=HTTPStatus.CONFLICT,
        expected_json_content={"message": "User with email already exists."},
    )
