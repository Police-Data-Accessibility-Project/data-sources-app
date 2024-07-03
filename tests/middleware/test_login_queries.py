import uuid
from http import HTTPStatus
from unittest.mock import patch, MagicMock

import psycopg2
import pytest

from middleware.login_queries import (
    get_user_info,
    create_session_token,
    get_session_token_user_data,
    is_admin,
    generate_api_key,
    get_api_key_for_user,
    refresh_session,
)
from middleware.custom_exceptions import UserNotFoundError, TokenNotFoundError
from tests.helper_functions import create_test_user, DynamicMagicMock
from tests.fixtures import db_cursor, dev_db_connection


def test_login_query(db_cursor: psycopg2.extensions.cursor) -> None:
    """
    Test the login query by comparing the password digest for a user retrieved from the database
    with the password hash of a test user.

    :param db_cursor: The database cursor to execute the query.
    :return: None
    """
    test_user = create_test_user(db_cursor)

    user_data = get_user_info(db_cursor, test_user.email)

    assert user_data["password_digest"] == test_user.password_hash


def test_login_results_user_not_found(db_cursor: psycopg2.extensions.cursor) -> None:
    """UserNotFoundError should be raised if the user does not exist in the database"""
    with pytest.raises(UserNotFoundError):
        get_user_info(cursor=db_cursor, email="nonexistent@example.com")


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


def test_is_admin_happy_path() -> None:
    """
    Creates and inserts two users, one an admin and the other not
    And then checks to see if the `is_admin` properly
    identifies both
    :param db_cursor:
    """
    mock_db_client = MagicMock()
    mock_get_role_by_email_result = MagicMock()
    mock_get_role_by_email_result.role = "admin"
    mock_db_client.get_role_by_email.return_value = mock_get_role_by_email_result

    result = is_admin(mock_db_client, "test_email")
    assert result is True
    mock_db_client.get_role_by_email.assert_called_once_with("test_email")

def test_is_admin_not_admin() -> None:
    """
    Creates and inserts two users, one an admin and the other not
    And then checks to see if the `is_admin` properly
    identifies both
    :param db_cursor:
    """
    mock_db_client = MagicMock()
    mock_get_role_by_email_result = MagicMock()
    mock_get_role_by_email_result.role = "user"
    mock_db_client.get_role_by_email.return_value = mock_get_role_by_email_result

    result = is_admin(mock_db_client, "test_email")
    assert result is False
    mock_db_client.get_role_by_email.assert_called_once_with("test_email")


def test_token_results_raises_token_not_found_error(db_cursor):
    """token_results() should raise TokenNotFoundError for nonexistent token"""
    with pytest.raises(TokenNotFoundError):
        get_session_token_user_data(cursor=db_cursor, token=str(uuid.uuid4()))


def test_generate_api_key():
    api_key = generate_api_key()
    assert len(api_key) == 32
    assert all(c in "0123456789abcdef" for c in api_key)


def test_get_api_key_for_user_success(monkeypatch):
    (
        mock_check_password_hash,
        mock_cursor,
        mock_email,
        mock_generate_api_key,
        mock_get_user_info,
        mock_make_response,
        mock_password,
        mock_password_digest,
        mock_update_api_key,
        mock_user_id,
    ) = setup_mocks(monkeypatch)
    mock_check_password_hash.return_value = True
    mock_api_key = MagicMock()
    mock_generate_api_key.return_value = mock_api_key
    get_api_key_for_user(mock_cursor, mock_email, mock_password)

    mock_get_user_info.assert_called_with(mock_cursor, mock_email)
    mock_check_password_hash.assert_called_with(mock_password_digest, mock_password)
    mock_generate_api_key.assert_called()
    mock_update_api_key.assert_called_with(mock_cursor, mock_api_key, str(mock_user_id))
    mock_make_response.assert_called_with({"api_key": mock_api_key}, HTTPStatus.OK)


def test_get_api_key_for_user_failure(monkeypatch):
    (
        mock_check_password_hash,
        mock_cursor,
        mock_email,
        mock_generate_api_key,
        mock_get_user_info,
        mock_make_response,
        mock_password,
        mock_password_digest,
        mock_update_api_key,
        mock_user_id,
    ) = setup_mocks(monkeypatch)

    mock_check_password_hash.return_value = False

    get_api_key_for_user(mock_cursor, mock_email, mock_password)

    mock_get_user_info.assert_called_with(mock_cursor, mock_email)
    mock_check_password_hash.assert_called_with(mock_password_digest, mock_password)
    mock_generate_api_key.assert_not_called()
    mock_update_api_key.assert_not_called()
    mock_make_response.assert_called_with(
        {"message": "Invalid email or password"}, HTTPStatus.UNAUTHORIZED
    )


def setup_mocks(monkeypatch):
    mock_cursor = MagicMock()
    mock_email = MagicMock()
    mock_password = MagicMock()
    mock_password_digest = MagicMock()
    mock_user_id = 123
    mock_user_data = {
        "id": mock_user_id,
        "password_digest": mock_password_digest,
    }
    mock_get_user_info = MagicMock(return_value=mock_user_data)
    mock_check_password_hash = MagicMock()
    mock_api_key = MagicMock()
    mock_generate_api_key = MagicMock(return_value=mock_api_key)
    mock_update_api_key = MagicMock()
    mock_make_response = MagicMock()
    monkeypatch.setattr("middleware.login_queries.get_user_info", mock_get_user_info)
    monkeypatch.setattr(
        "middleware.login_queries.check_password_hash", mock_check_password_hash
    )
    monkeypatch.setattr(
        "middleware.login_queries.generate_api_key", mock_generate_api_key
    )
    monkeypatch.setattr("middleware.login_queries.update_api_key", mock_update_api_key)
    monkeypatch.setattr("middleware.login_queries.make_response", mock_make_response)
    return (
        mock_check_password_hash,
        mock_cursor,
        mock_email,
        mock_generate_api_key,
        mock_get_user_info,
        mock_make_response,
        mock_password,
        mock_password_digest,
        mock_update_api_key,
        mock_user_id,
    )


class RefreshSessionMocks(DynamicMagicMock):
    cursor: MagicMock
    old_token: MagicMock
    new_token: MagicMock
    get_session_token_user_data: MagicMock
    user_data: MagicMock
    delete_session_token: MagicMock
    make_response: MagicMock
    create_session_token: MagicMock
    mock_user_id: MagicMock
    mock_email: MagicMock


@pytest.fixture
def setup_refresh_session_mocks(monkeypatch):
    mock = RefreshSessionMocks()
    mock.get_session_token_user_data.return_value = mock.user_data
    mock.create_session_token.return_value = mock.new_token
    mock.user_data.id = mock.mock_user_id
    mock.user_data.email = mock.mock_email

    monkeypatch.setattr(
        "middleware.login_queries.get_session_token_user_data",
        mock.get_session_token_user_data,
    )
    monkeypatch.setattr(
        "middleware.login_queries.delete_session_token", mock.delete_session_token
    )
    monkeypatch.setattr("middleware.login_queries.make_response", mock.make_response)
    monkeypatch.setattr(
        "middleware.login_queries.create_session_token", mock.create_session_token
    )
    return mock


def test_refresh_session_happy_path(setup_refresh_session_mocks):
    mock = setup_refresh_session_mocks
    refresh_session(mock.cursor, mock.old_token)
    mock.get_session_token_user_data.assert_called_with(mock.cursor, mock.old_token)
    mock.delete_session_token.assert_called_with(mock.cursor, mock.old_token)
    mock.create_session_token.assert_called_with(
        mock.cursor, mock.user_data.id, mock.user_data.email
    )
    mock.make_response.assert_called_with(
        {"message": "Successfully refreshed session token", "data": mock.new_token},
        HTTPStatus.OK,
    )


def test_refresh_session_token_not_found_error(setup_refresh_session_mocks):
    mock = setup_refresh_session_mocks
    mock.get_session_token_user_data.side_effect = TokenNotFoundError
    refresh_session(mock.cursor, mock.old_token)
    mock.get_session_token_user_data.assert_called_with(mock.cursor, mock.old_token)
    mock.delete_session_token.assert_not_called()
    mock.create_session_token.assert_not_called()
    mock.make_response.assert_called_with(
        {"message": "Invalid session token"}, HTTPStatus.FORBIDDEN
    )
