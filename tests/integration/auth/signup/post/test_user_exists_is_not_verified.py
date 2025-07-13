from http import HTTPStatus


def test_signup_post_user_exists_is_not_verified(
    helper
):
    """
    If a user signs up with an email that exists but is not verified
    that user should receive a special error message reminding them to
    validate their email.
    """
    # Try signing up a user that already exists but is not verified

    helper.signup_user()

    helper.signup_user(
        expected_response_status=HTTPStatus.CONFLICT,
        expected_json_content={
            "message": "User with email has already signed up. "
            "Please validate your email or request a new validation email."
        },
    )
