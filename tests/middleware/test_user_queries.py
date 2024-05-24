import psycopg2
import pytest

from middleware.custom_exceptions import UserNotFoundError
from middleware.user_queries import user_post_results, user_check_email
from tests.middleware.helper_functions import create_test_user
from tests.middleware.fixtures import dev_db_connection, db_cursor


def test_user_post_query(db_cursor: psycopg2.extensions.cursor) -> None:
    """
    Test the `user_post_query` method, ensuring it properly returns the expected results

    :param db_cursor: The database cursor.
    :return: None.
    """
    user_post_results(db_cursor, "unit_test", "unit_test")

    db_cursor.execute(f"SELECT email FROM users WHERE email = 'unit_test'")
    email_check = db_cursor.fetchone()[0]

    assert email_check == "unit_test"


def test_user_check_email(db_cursor: psycopg2.extensions.cursor) -> None:
    """
    Verify the functionality of the `user_check_email` method.

    :param db_cursor: A `psycopg2.extensions.cursor` object representing the database cursor.
    :return: None

    """
    user = create_test_user(db_cursor)
    user_data = user_check_email(db_cursor, user.email)
    assert user_data["id"] == user.id

def test_user_check_email_raises_user_not_found_error(db_cursor: psycopg2.extensions) -> None:
    with pytest.raises(UserNotFoundError):
        user_check_email(db_cursor, "nonexistent@example.com")