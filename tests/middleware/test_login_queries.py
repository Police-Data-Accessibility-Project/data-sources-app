from unittest.mock import patch

import psycopg2

from middleware.login_queries import login_results, create_session_token, token_results, is_admin
from tests.middleware.helper_functions import create_test_user
from tests.middleware.fixtures import dev_db_connection, db_cursor

def test_login_query(db_cursor: psycopg2.extensions.cursor) -> None:
    """
    Test the login query by comparing the password digest for a user retrieved from the database
    with the password hash of a test user.

    :param db_cursor: The database cursor to execute the query.
    :return: None
    """
    test_user = create_test_user(db_cursor)

    user_data = login_results(db_cursor, "example@example.com")

    assert user_data["password_digest"] == test_user.password_hash


def test_create_session_token_results(db_cursor: psycopg2.extensions.cursor) -> None:
    """
    Tests the `create_session_token_results` method properly
    creates the expected session token in the database,
    associated with the proper user.

    :param db_cursor: The psycopg2 database cursor object.
    :return: None
    """
    test_user = create_test_user(db_cursor)
    with patch("os.getenv", return_value="mysecretkey") as mock_getenv:
        token = create_session_token(db_cursor, test_user.id, test_user.email)
    new_token = token_results(db_cursor, token)

    assert new_token["email"] == test_user.email


def test_is_admin(db_cursor: psycopg2.extensions.cursor) -> None:
    """
    Creates and inserts two users, one an admin and the other not
    And then checks to see if the `is_admin` properly
    identifies both
    :param db_cursor:
    """
    regular_user = create_test_user(db_cursor)
    admin_user = create_test_user(
        cursor=db_cursor, email="admin@admin.com", role="admin"
    )
    assert is_admin(db_cursor, admin_user.email)
    assert not is_admin(db_cursor, regular_user.email)
