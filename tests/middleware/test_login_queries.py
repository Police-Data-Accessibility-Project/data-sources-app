import uuid
from unittest.mock import patch

import psycopg2
import pytest

from middleware.login_queries import (
    login_results,
    create_session_token,
    get_session_token_user_data,
    is_admin,
)
from middleware.custom_exceptions import UserNotFoundError, TokenNotFoundError
from tests.helper_functions import create_test_user
from tests.fixtures import db_cursor, dev_db_connection


def test_login_query(db_cursor: psycopg2.extensions.cursor) -> None:
    """
    Test the login query by comparing the password digest for a user retrieved from the database
    with the password hash of a test user.

    :param db_cursor: The database cursor to execute the query.
    :return: None
    """
    test_user = create_test_user(db_cursor)

    user_data = login_results(db_cursor, test_user.email)

    assert user_data["password_digest"] == test_user.password_hash


def test_login_results_user_not_found(db_cursor: psycopg2.extensions.cursor) -> None:
    """UserNotFoundError should be raised if the user does not exist in the database"""
    with pytest.raises(UserNotFoundError):
        login_results(cursor=db_cursor, email="nonexistent@example.com")


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
    new_token = get_session_token_user_data(db_cursor, token)

    assert new_token.email == test_user.email


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


def test_is_admin_raises_user_not_logged_in_error(db_cursor):
    """
    Check that when searching for a user by an email that doesn't exist,
    the UserNotFoundError is raised
    :return:
    """
    with pytest.raises(UserNotFoundError):
        is_admin(cursor=db_cursor, email=str(uuid.uuid4()))


def test_token_results_raises_token_not_found_error(db_cursor):
    """token_results() should raise TokenNotFoundError for nonexistent token"""
    with pytest.raises(TokenNotFoundError):
        get_session_token_user_data(cursor=db_cursor, token=str(uuid.uuid4()))
