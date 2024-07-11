from unittest.mock import MagicMock

import psycopg2
import pytest

from middleware.custom_exceptions import UserNotFoundError
from middleware.user_queries import user_post_results, user_check_email
from tests.helper_functions import create_test_user, DynamicMagicMock
from tests.fixtures import db_cursor, dev_db_connection


def test_user_post_query(monkeypatch):

    mock_db_client = MagicMock()
    mock_generate_password_hash = MagicMock()
    mock_generate_password_hash.return_value = "password_digest"

    monkeypatch.setattr(
        "middleware.user_queries.generate_password_hash", mock_generate_password_hash
    )

    user_post_results(mock_db_client, "test_email", "test_password")

    mock_generate_password_hash.assert_called_once_with("test_password")
    mock_db_client.add_new_user.assert_called_once_with("test_email", "password_digest")


class TestUserMagicMock(DynamicMagicMock):
    db_client: MagicMock
    user_id: MagicMock
    email: MagicMock


def test_user_check_email(monkeypatch) -> None:
    """
    Verify the functionality of the `user_check_email` method.

    :param db_cursor: A `psycopg2.extensions.cursor` object representing the database cursor.
    :return: None

    """
    mock = TestUserMagicMock()
    mock.db_client.get_user_id.return_value = mock.user_id

    user_check_email(mock.db_client, mock.email)
    mock.db_client.get_user_id.assert_called_once_with(mock.email)


def test_user_check_email_raises_user_not_found_error(monkeypatch) -> None:
    mock = TestUserMagicMock()
    mock.db_client.get_user_id.return_value = None

    with pytest.raises(UserNotFoundError):
        user_check_email(mock.db_client, mock.email)
    mock.db_client.get_user_id.assert_called_once_with(mock.email)
