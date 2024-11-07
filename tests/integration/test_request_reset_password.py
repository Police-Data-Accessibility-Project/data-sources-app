"""Integration tests for /request-reset-password endpoint."""

from http import HTTPStatus
import psycopg

from database_client.database_client import DatabaseClient
from tests.conftest import flask_client_with_db
from tests.helper_scripts.helper_functions import (
    create_test_user_api,
)
from tests.helper_scripts.run_and_validate_request import run_and_validate_request
from tests.helper_scripts.simple_result_validators import check_response_status


def test_request_reset_password_post(flask_client_with_db, mocker):
    """
    Test that POST call to /request-reset-password endpoint successfully initiates a password reset request, sends a single email via Mailgun, and verifies the reset token is correctly associated with the user's email in the database
    """

    user_info = create_test_user_api(flask_client_with_db)

    mock_send_password_reset_link = mocker.patch(
        "middleware.primary_resource_logic.reset_token_queries.send_password_reset_link"
    )
    response_json = run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="post",
        endpoint="/api/request-reset-password",
        json={"email": user_info.email},
    )

    reset_token = response_json.get("token")
    assert mock_send_password_reset_link.called_once_with(user_info.email, reset_token)

    db_client = DatabaseClient()
    rows = db_client.execute_raw_sql(
        """
    SELECT email FROM reset_tokens where token = %s
    """,
        (reset_token,),
    )
    assert (
        len(rows) == 1
    ), "Only one row should have a reset token associated with this email"
    email = rows[0]["email"]
    assert (
        email == user_info.email
    ), "Email associated with reset token should match the user's email"
