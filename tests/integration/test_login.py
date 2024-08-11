"""Integration tests for /login endpoint"""

import psycopg2.extensions

from database_client.database_client import DatabaseClient
from tests.fixtures import dev_db_connection, flask_client_with_db
from tests.helper_scripts.helper_functions import (
    create_test_user_api,
    login_and_return_api_key,
    assert_api_key_exists_for_email,
)


def test_login_post(flask_client_with_db, dev_db_connection: psycopg2.extensions.connection):
    """
    Test that POST call to /login endpoint successfully logs in a user, creates a session token, and verifies the session token exists only once in the database with the correct email
    """
    # Create user
    user_info = create_test_user_api(flask_client_with_db)
    api_key = login_and_return_api_key(flask_client_with_db, user_info)
    db_client = DatabaseClient(dev_db_connection.cursor())
    assert_api_key_exists_for_email(
        db_client=db_client, api_key=api_key, email=user_info.email
    )
