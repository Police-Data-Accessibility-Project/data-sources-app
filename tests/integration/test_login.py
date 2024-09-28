"""Integration tests for /login endpoint"""

import psycopg
from flask_jwt_extended import get_jwt_identity, decode_token

from database_client.database_client import DatabaseClient
from tests.conftest import dev_db_connection, flask_client_with_db
from tests.helper_scripts.helper_functions import (
    create_test_user_api,
    login_and_return_jwt_tokens,
)
from tests.helper_scripts.common_test_functions import assert_api_key_exists_for_email, \
    assert_jwt_token_matches_user_email


def test_login_post(
    flask_client_with_db, dev_db_connection: psycopg.Connection
):
    """
    Test that POST call to /login endpoint successfully logs in a user, creates a session token, and verifies the session token exists only once in the database with the correct email
    """
    # Create user
    user_info = create_test_user_api(flask_client_with_db)
    jwt_tokens = login_and_return_jwt_tokens(flask_client_with_db, user_info)
    assert_jwt_token_matches_user_email(
        email=user_info.email,
        jwt_token=jwt_tokens.access_token,
    )
