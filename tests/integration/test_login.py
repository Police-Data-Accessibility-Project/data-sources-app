"""Integration tests for /login endpoint"""

import psycopg2.extensions

from tests.fixtures import dev_db_connection, client_with_db
from tests.helper_functions import create_test_user_api, login_and_return_session_token


def test_login_post(client_with_db, dev_db_connection: psycopg2.extensions.connection):
    """
    Test that POST call to /login endpoint successfully logs in a user, creates a session token, and verifies the session token exists only once in the database with the correct email
    """
    # Create user
    user_info = create_test_user_api(client_with_db)
    session_token = login_and_return_session_token(client_with_db, user_info)

    cursor = dev_db_connection.cursor()
    cursor.execute(
        """
        SELECT email from session_tokens WHERE token = %s
        """,
        (session_token,),
    )
    rows = cursor.fetchall()
    assert len(rows) == 1, "Session token should only exist once in database"

    row = rows[0]
    assert (
        row[0] == user_info.email
    ), "Email in session_tokens table does not match user email"
