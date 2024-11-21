"""Integration tests for /request-reset-password endpoint."""

from database_client.database_client import DatabaseClient
from middleware.SimpleJWT import SimpleJWT, JWTPurpose
from resources.endpoint_schema_config import SchemaConfigs
from tests.helper_scripts.helper_classes.TestDataCreatorFlask import TestDataCreatorFlask
from conftest import test_data_creator_flask, monkeysession

def test_request_reset_password_post(test_data_creator_flask: TestDataCreatorFlask, mocker):
    """
    Test that POST call to /request-reset-password endpoint successfully initiates a password reset request, sends a single email via Mailgun, and verifies the reset token is correctly associated with the user's email in the database
    """
    tdc = test_data_creator_flask

    user_info = tdc.standard_user().user_info

    mock_send_password_reset_link = mocker.patch(
        "middleware.primary_resource_logic.reset_token_queries.send_password_reset_link"
    )
    tdc.request_validator.post(
        endpoint="/api/request-reset-password",
        json={"email": user_info.email},
        expected_schema=SchemaConfigs.REQUEST_RESET_PASSWORD.value.primary_output_schema,
    )

    reset_token = mock_send_password_reset_link.call_args[1]['token']
    assert mock_send_password_reset_link.called_once_with(user_info.email, reset_token)
    decoded_token = SimpleJWT.decode(
        token=reset_token,
        purpose=JWTPurpose.PASSWORD_RESET
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
