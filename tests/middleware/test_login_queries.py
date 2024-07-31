import uuid
from http import HTTPStatus
from unittest.mock import patch, MagicMock

import psycopg2
import pytest
from flask import Response

from database_client.database_client import DatabaseClient
from database_client.enums import ExternalAccountTypeEnum
from middleware.login_queries import (
    create_session_token,
    is_admin,
    generate_api_key,
    get_api_key_for_user,
    refresh_session,
    try_logging_in_with_github_id,
)
from middleware.custom_exceptions import UserNotFoundError, TokenNotFoundError
from tests.helper_functions import create_test_user, DynamicMagicMock
from tests.fixtures import db_cursor, dev_db_connection


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


def test_generate_api_key():
    api_key = generate_api_key()
    assert len(api_key) == 32
    assert all(c in "0123456789abcdef" for c in api_key)


def test_get_api_key_for_user_success(monkeypatch):
    (
        mock_check_password_hash,
        mock_db_client,
        mock_email,
        mock_generate_api_key,
        mock_make_response,
        mock_password,
        mock_password_digest,
        mock_update_api_key,
        mock_user_id,
    ) = setup_mocks(monkeypatch)
    mock_check_password_hash.return_value = True
    mock_api_key = MagicMock()
    mock_generate_api_key.return_value = mock_api_key

    # Call function
    get_api_key_for_user(mock_db_client, mock_email, mock_password)

    mock_db_client.get_user_info.assert_called_with(mock_email)
    mock_check_password_hash.assert_called_with(mock_password_digest, mock_password)
    mock_generate_api_key.assert_called()
    mock_db_client.update_user_api_key.assert_called_with(
        user_id=mock_user_id, api_key=mock_api_key
    )
    mock_make_response.assert_called_with({"api_key": mock_api_key}, HTTPStatus.OK)


def test_get_api_key_for_user_failure(monkeypatch):
    (
        mock_check_password_hash,
        mock_db_client,
        mock_email,
        mock_generate_api_key,
        mock_make_response,
        mock_password,
        mock_password_digest,
        mock_update_api_key,
        mock_user_id,
    ) = setup_mocks(monkeypatch)

    mock_check_password_hash.return_value = False

    get_api_key_for_user(mock_db_client, mock_email, mock_password)

    mock_db_client.get_user_info.assert_called_with(mock_email)
    mock_check_password_hash.assert_called_with(mock_password_digest, mock_password)
    mock_generate_api_key.assert_not_called()
    mock_db_client.update_user_api_key.assert_not_called()
    mock_make_response.assert_called_with(
        {"message": "Invalid email or password"}, HTTPStatus.UNAUTHORIZED
    )


def setup_mocks(monkeypatch):
    mock_db_client = MagicMock()
    mock_email = MagicMock()
    mock_password = MagicMock()
    mock_password_digest = MagicMock()
    mock_user_id = 123
    mock_user_data = DatabaseClient.UserInfo(
        id=mock_user_id,
        password_digest=mock_password_digest,
        api_key=None,
        email=mock_email,
    )
    mock_db_client.get_user_info.return_value = mock_user_data
    mock_check_password_hash = MagicMock()
    mock_api_key = MagicMock()
    mock_generate_api_key = MagicMock(return_value=mock_api_key)
    mock_update_api_key = MagicMock()
    mock_make_response = MagicMock()
    monkeypatch.setattr(
        "middleware.login_queries.check_password_hash", mock_check_password_hash
    )
    monkeypatch.setattr(
        "middleware.login_queries.generate_api_key", mock_generate_api_key
    )
    monkeypatch.setattr("middleware.login_queries.make_response", mock_make_response)
    return (
        mock_check_password_hash,
        mock_db_client,
        mock_email,
        mock_generate_api_key,
        mock_make_response,
        mock_password,
        mock_password_digest,
        mock_update_api_key,
        mock_user_id,
    )


class RefreshSessionMocks(DynamicMagicMock):
    db_client: MagicMock
    old_token: MagicMock
    new_token: MagicMock
    get_session_token_user_data: MagicMock
    session_token_info: MagicMock
    delete_session_token: MagicMock
    make_response: MagicMock
    create_session_token: MagicMock
    mock_user_id: MagicMock
    mock_email: MagicMock


@pytest.fixture
def setup_refresh_session_mocks(monkeypatch):
    mock = RefreshSessionMocks()
    mock.db_client.get_session_token_info.return_value = mock.session_token_info
    mock.create_session_token.return_value = mock.new_token
    mock.session_token_info.id = mock.mock_user_id
    mock.session_token_info.email = mock.mock_email

    monkeypatch.setattr("middleware.login_queries.make_response", mock.make_response)
    monkeypatch.setattr(
        "middleware.login_queries.create_session_token", mock.create_session_token
    )
    return mock


def test_refresh_session_happy_path(setup_refresh_session_mocks):
    mock = setup_refresh_session_mocks
    refresh_session(mock.db_client, mock.old_token)
    mock.db_client.get_session_token_info.assert_called_with(mock.old_token)
    mock.db_client.delete_session_token.assert_called_with(mock.old_token)
    mock.create_session_token.assert_called_with(
        mock.db_client, mock.session_token_info.id, mock.session_token_info.email
    )
    mock.make_response.assert_called_with(
        {"message": "Successfully refreshed session token", "data": mock.new_token},
        HTTPStatus.OK,
    )


def test_refresh_session_token_not_found_error(setup_refresh_session_mocks):
    mock = setup_refresh_session_mocks
    mock.db_client.get_session_token_info.return_value = None
    refresh_session(mock.db_client, mock.old_token)
    mock.db_client.get_session_token_info.assert_called_with(mock.old_token)
    mock.delete_session_token.assert_not_called()
    mock.create_session_token.assert_not_called()
    mock.make_response.assert_called_with(
        {"message": "Invalid session token"}, HTTPStatus.FORBIDDEN
    )


class TryLoggingInWithGithubIdMocks(DynamicMagicMock):
    db_client: MagicMock
    github_user_info: MagicMock
    github_user_id: MagicMock
    unauthorized_response: MagicMock
    login_response: MagicMock
    user_info: MagicMock


PATCH_PREFIX = "middleware.login_queries."

TRY_LOGGING_IN_WITH_GITHUB_ID_PATCH_PATHS = {
    "unauthorized_response": f"{PATCH_PREFIX}unauthorized_response",
    "login_response": f"{PATCH_PREFIX}login_response",
}

TRY_LOGGING_IN_WITH_GITHUB_ID_RETURN_VALUES = {
    "unauthorized_response": MagicMock(spec=Response),
    "login_response": MagicMock(spec=Response),
}


def test_try_logging_in_with_github_id_happy_path():
    mock = TryLoggingInWithGithubIdMocks(
        patch_paths=TRY_LOGGING_IN_WITH_GITHUB_ID_PATCH_PATHS,
    )
    mock.github_user_info.user_id = mock.github_user_id
    mock.db_client.get_user_info_by_external_account_id.return_value = mock.user_info

    result = try_logging_in_with_github_id(mock.db_client, mock.github_user_info)

    assert result == mock.login_response.return_value

    mock.db_client.get_user_info_by_external_account_id.assert_called_with(
        external_account_id=mock.github_user_id,
        external_account_type=ExternalAccountTypeEnum.GITHUB
    )
    mock.login_response.assert_called_once_with(mock.db_client, mock.user_info)

def test_try_logging_in_with_github_id_unauthorized():
    mock = TryLoggingInWithGithubIdMocks(
        patch_paths=TRY_LOGGING_IN_WITH_GITHUB_ID_PATCH_PATHS,
        return_values=TRY_LOGGING_IN_WITH_GITHUB_ID_RETURN_VALUES
    )
    mock.github_user_info.user_id = mock.github_user_id
    mock.db_client.get_user_info_by_external_account_id.return_value = None

    result = try_logging_in_with_github_id(mock.db_client, mock.github_user_info)

    assert result == mock.unauthorized_response.return_value

    mock.db_client.get_user_info_by_external_account_id.assert_called_with(
        external_account_id=mock.github_user_id,
        external_account_type=ExternalAccountTypeEnum.GITHUB
    )
    mock.unauthorized_response.assert_called_once()