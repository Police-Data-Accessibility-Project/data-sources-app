from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from flask import Response

from database_client.database_client import DatabaseClient
from database_client.enums import ExternalAccountTypeEnum
from middleware.login_queries import (
    is_admin,
    generate_api_key,
    get_api_key_for_user,
    refresh_session,
    try_logging_in_with_github_id,
)
from tests.helper_scripts.DymamicMagicMock import DynamicMagicMock


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
    mock = setup_get_api_for_user_mocks()
    mock.check_password_hash.return_value = True
    mock.generate_api_key.return_value = mock.api_key

    # Call function
    get_api_key_for_user(mock.db_client, mock.email, mock.password)

    mock.db_client.get_user_info.assert_called_with(mock.email)
    mock.check_password_hash.assert_called_with(mock.password_digest, mock.password)
    mock.generate_api_key.assert_called()
    mock.db_client.update_user_api_key.assert_called_with(
        user_id=mock.user_id, api_key=mock.api_key
    )
    mock.make_response.assert_called_with({"api_key": mock.api_key}, HTTPStatus.OK)


def test_get_api_key_for_user_failure(monkeypatch):
    mock = setup_get_api_for_user_mocks()

    mock.check_password_hash.return_value = False

    get_api_key_for_user(mock.db_client, mock.email, mock.password)

    mock.db_client.get_user_info.assert_called_with(mock.email)
    mock.check_password_hash.assert_called_with(mock.password_digest, mock.password)
    mock.generate_api_key.assert_not_called()
    mock.db_client.update_user_api_key.assert_not_called()
    mock.make_response.assert_called_with(
        {"message": "Invalid email or password"}, HTTPStatus.UNAUTHORIZED
    )


class GetAPIKeyForUserMocks(DynamicMagicMock):
    db_client: MagicMock
    email: MagicMock
    password: MagicMock
    password_digest: MagicMock
    user_id: MagicMock
    user_data: MagicMock
    check_password_hash: MagicMock
    generate_api_key: MagicMock
    update_api_key: MagicMock
    make_response: MagicMock
    api_key = MagicMock()


def setup_get_api_for_user_mocks():
    mock = GetAPIKeyForUserMocks(
        patch_root="middleware.login_queries",
        mocks_to_patch=[
            "check_password_hash",
            "generate_api_key",
            "make_response",
        ],
    )

    mock.db_client.get_user_info.return_value = DatabaseClient.UserInfo(
        id=mock.user_id,
        password_digest=mock.password_digest,
        api_key=None,
        email=mock.email,
    )
    mock.generate_api_key.return_value = mock.api_key
    return mock


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
    mock = RefreshSessionMocks(
        patch_root="middleware.login_queries",
        mocks_to_patch=["make_response", "create_session_token"],
    )
    mock.db_client.get_session_token_info.return_value = mock.session_token_info
    mock.create_session_token.return_value = mock.new_token
    mock.session_token_info.id = mock.mock_user_id
    mock.session_token_info.email = mock.mock_email

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


def test_try_logging_in_with_github_id_happy_path():
    mock = TryLoggingInWithGithubIdMocks(
        patch_root="middleware.login_queries",
        mocks_to_patch=["unauthorized_response", "login_response"],
    )
    mock.github_user_info.user_id = mock.github_user_id
    mock.db_client.get_user_info_by_external_account_id.return_value = mock.user_info

    result = try_logging_in_with_github_id(mock.db_client, mock.github_user_info)

    assert result == mock.login_response.return_value

    mock.db_client.get_user_info_by_external_account_id.assert_called_with(
        external_account_id=mock.github_user_id,
        external_account_type=ExternalAccountTypeEnum.GITHUB,
    )
    mock.login_response.assert_called_once_with(mock.db_client, mock.user_info)


def test_try_logging_in_with_github_id_unauthorized():
    mock = TryLoggingInWithGithubIdMocks(
        patch_root="middleware.login_queries",
        mocks_to_patch=["unauthorized_response", "login_response"],
        return_values={
            "unauthorized_response": MagicMock(spec=Response),
            "login_response": MagicMock(spec=Response),
        },
    )
    mock.github_user_info.user_id = mock.github_user_id
    mock.db_client.get_user_info_by_external_account_id.return_value = None

    result = try_logging_in_with_github_id(mock.db_client, mock.github_user_info)

    assert result == mock.unauthorized_response.return_value

    mock.db_client.get_user_info_by_external_account_id.assert_called_with(
        external_account_id=mock.github_user_id,
        external_account_type=ExternalAccountTypeEnum.GITHUB,
    )
    mock.unauthorized_response.assert_called_once()
