"""Integration tests for /reset-password endpoint."""

from http import HTTPStatus
import uuid

import psycopg2

from tests.fixtures import dev_db_connection, flask_client_with_db
from tests.helper_scripts.helper_functions import (
    create_test_user_api,
    get_user_password_digest,
    request_reset_password_api,
    check_response_status,
    run_and_validate_request,
)


def test_reset_password_post(
    flask_client_with_db, dev_db_connection: psycopg2.extensions.connection, mocker
):
    """
    Test that POST call to /reset-password endpoint successfully resets the user's password, and verifies the new password digest is distinct from the old one in the database
    """

    user_info = create_test_user_api(flask_client_with_db)
    cursor = dev_db_connection.cursor()
    old_password_digest = get_user_password_digest(cursor, user_info)

    token = request_reset_password_api(flask_client_with_db, mocker, user_info)
    new_password = str(uuid.uuid4())
    run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="post",
        endpoint="/api/reset-password",
        json={"email": user_info.email, "token": token, "password": new_password},
    )
    new_password_digest = get_user_password_digest(cursor, user_info)
    assert (
        new_password_digest != old_password_digest
    ), "Old and new password digests should be distinct"
