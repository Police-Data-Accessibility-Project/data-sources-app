"""Integration tests for /login endpoint"""

import psycopg2.extensions

from tests.fixtures import dev_db_connection, client_with_db
from tests.helper_functions import create_test_user_api, login_and_return_session_token, \
    assert_session_token_exists_for_email


def test_login_post(client_with_db, dev_db_connection: psycopg2.extensions.connection):
    """
    Test that POST call to /login endpoint successfully logs in a user, creates a session token, and verifies the session token exists only once in the database with the correct email
    """
    # Create user
    user_info = create_test_user_api(client_with_db)
    session_token = login_and_return_session_token(client_with_db, user_info)

    assert_session_token_exists_for_email(
        cursor=dev_db_connection.cursor(), session_token=session_token, email=user_info.email
    )