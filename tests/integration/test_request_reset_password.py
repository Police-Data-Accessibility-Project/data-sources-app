"""Integration tests for /request-reset-password endpoint."""

from http import HTTPStatus
import psycopg

from tests.fixtures import dev_db_connection, flask_client_with_db
from tests.helper_scripts.helper_functions import (
    create_test_user_api,
)
from tests.helper_scripts.common_test_functions import check_response_status, run_and_validate_request


def test_request_reset_password_post(
    flask_client_with_db, dev_db_connection: psycopg.Connection, mocker
):
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

    cursor = dev_db_connection.cursor()
    cursor.execute(
        """
    SELECT email FROM reset_tokens where token = %s
    """,
        (reset_token,),
    )
    rows = cursor.fetchall()
    assert (
        len(rows) == 1
    ), "Only one row should have a reset token associated with this email"
    email = rows[0][0]
    assert (
        email == user_info.email
    ), "Email associated with reset token should match the user's email"
