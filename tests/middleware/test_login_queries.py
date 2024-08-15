from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from flask import Response

from database_client.database_client import DatabaseClient
from database_client.enums import ExternalAccountTypeEnum
from middleware.login_queries import (
    generate_api_key,
    get_api_key_for_user,
    refresh_session,
    try_logging_in_with_github_id,
)
from tests.helper_scripts.DymamicMagicMock import DynamicMagicMock


def test_generate_api_key():
    api_key = generate_api_key()
    assert len(api_key) == 32
    assert all(c in "0123456789abcdef" for c in api_key)


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


def test_get_api_key_for_user_success(monkeypatch):
    mock = setup_get_api_for_user_mocks()
    mock.check_password_hash.return_value = True
    mock.generate_api_key.return_value = mock.api_key

    # Call function
    get_api_key_for_user(mock.db_client, mock.email, mock.password)

    assert_get_api_key_for_user_precondition_calls(mock)

    mock.generate_api_key.assert_called()
    mock.db_client.update_user_api_key.assert_called_with(
        user_id=mock.user_id, api_key=mock.api_key
    )
    mock.make_response.assert_called_with({"api_key": mock.api_key}, HTTPStatus.OK)


def test_get_api_key_for_user_failure():
    mock = setup_get_api_for_user_mocks()

    mock.check_password_hash.return_value = False

    get_api_key_for_user(mock.db_client, mock.email, mock.password)

    assert_get_api_key_for_user_precondition_calls(mock)

    mock.generate_api_key.assert_not_called()
    mock.db_client.update_user_api_key.assert_not_called()
    mock.make_response.assert_called_with(
        {"message": "Invalid email or password"}, HTTPStatus.UNAUTHORIZED
    )


def assert_get_api_key_for_user_precondition_calls(mock: GetAPIKeyForUserMocks):
    mock.db_client.get_user_info.assert_called_with(mock.email)
    mock.check_password_hash.assert_called_with(mock.password_digest, mock.password)


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
def setup_refresh_session_mocks():
    mock = RefreshSessionMocks(
        patch_root="middleware.login_queries",
        mocks_to_patch=["make_response", "create_session_token"],
    )
    mock.db_client.get_session_token_info.return_value = mock.session_token_info
    mock.create_session_token.return_value = mock.new_token
    mock.session_token_info.id = mock.mock_user_id
    mock.session_token_info.email = mock.mock_email

    return mock


class TryLoggingInWithGithubIdMocks(DynamicMagicMock):
    db_client: MagicMock
    github_user_info: MagicMock
    github_user_id: MagicMock
    unauthorized_response: MagicMock
    login_response: MagicMock
    user_info: MagicMock


def assert_try_logging_in_with_github_id_precondition_calls(
    mock: TryLoggingInWithGithubIdMocks,
):
    mock.db_client.get_user_info_by_external_account_id.assert_called_with(
        external_account_id=mock.github_user_id,
        external_account_type=ExternalAccountTypeEnum.GITHUB,
    )


@pytest.fixture
def setup_try_logging_in_with_github_id_mocks():
    mock = TryLoggingInWithGithubIdMocks(
        patch_root="middleware.login_queries",
        mocks_to_patch=["unauthorized_response", "login_response"],
        return_values={
            "unauthorized_response": MagicMock(spec=Response),
            "login_response": MagicMock(spec=Response),
        },
    )

    mock.github_user_info.user_id = mock.github_user_id
    return mock

def test_try_logging_in_with_github_id_happy_path(setup_try_logging_in_with_github_id_mocks):
    mock = setup_try_logging_in_with_github_id_mocks

    mock.db_client.get_user_info_by_external_account_id.return_value = mock.user_info

    result = try_logging_in_with_github_id(mock.db_client, mock.github_user_info)

    assert_try_logging_in_with_github_id_precondition_calls(mock)

    assert result == mock.login_response.return_value
    mock.login_response.assert_called_once_with(mock.user_info)


def test_try_logging_in_with_github_id_unauthorized(setup_try_logging_in_with_github_id_mocks):
    mock = setup_try_logging_in_with_github_id_mocks

    mock.db_client.get_user_info_by_external_account_id.return_value = None

    result = try_logging_in_with_github_id(mock.db_client, mock.github_user_info)

    assert_try_logging_in_with_github_id_precondition_calls(mock)

    assert result == mock.unauthorized_response.return_value
    mock.unauthorized_response.assert_called_once()


class RefreshSessionMocks(DynamicMagicMock):
    identity: MagicMock
    get_jwt_identity: MagicMock
    create_access_token: MagicMock
    make_response: MagicMock
    access_token: MagicMock


def test_refresh_session():
    mock = RefreshSessionMocks(
        patch_root="middleware.login_queries",
        mocks_to_patch=["get_jwt_identity", "make_response", "create_access_token"],
    )
    mock.get_jwt_identity.return_value = mock.identity
    mock.create_access_token.return_value = mock.access_token

    refresh_session()

    mock.get_jwt_identity.assert_called_once()
    mock.create_access_token.assert_called_once_with(identity=mock.identity)
    mock.make_response.assert_called_once_with(
        {"message": "Successfully refreshed session token", "data": mock.access_token},
        HTTPStatus.OK,
    )
