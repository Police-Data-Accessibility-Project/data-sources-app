"""Integration tests for /request-reset-password endpoint."""

from db.client.core import DatabaseClient
from middleware.security.jwt.core import SimpleJWT
from middleware.security.jwt.enums import JWTPurpose
from tests.helper_scripts.helper_classes.TestDataCreatorFlask import (
    TestDataCreatorFlask,
)
from tests.conftest import test_data_creator_flask


def test_request_reset_password_post(
    test_data_creator_flask: TestDataCreatorFlask, mocker
):
    """
    Test that POST call to /request-reset-password endpoint successfully initiates a password reset request, sends a single email via Mailgun, and verifies the reset token is correctly associated with the user's email in the database
    """
    tdc = test_data_creator_flask

    user_info = tdc.standard_user().user_info

    token = tdc.request_validator.request_reset_password(
        email=user_info.email,
        mocker=mocker,
    )

    decoded_token = SimpleJWT.decode(
        token=token, expected_purpose=JWTPurpose.PASSWORD_RESET
    )

    db_client = DatabaseClient()
    rows = db_client.execute_raw_sql(
        """
    SELECT user_id FROM reset_tokens where token = %s
    """,
        (decoded_token.sub["token"],),
    )
    assert (
        len(rows) == 1
    ), "Only one row should have a reset token associated with this email"

    user_id = rows[0]["user_id"]
    assert (
        user_id == user_info.user_id
    ), "Email associated with reset token should match the user's email"


def test_request_password_reset_invalid_email(
    test_data_creator_flask: TestDataCreatorFlask, mocker
):
    tdc = test_data_creator_flask

    token = tdc.request_validator.request_reset_password(
        email="email_does_not_exist", mocker=mocker, expect_call=False
    )
