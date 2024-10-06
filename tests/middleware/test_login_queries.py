from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from flask import Response

from database_client.database_client import DatabaseClient
from database_client.enums import ExternalAccountTypeEnum
from middleware.primary_resource_logic.login_queries import (
    generate_api_key,
    get_api_key_for_user,
    refresh_session,
    try_logging_in_with_github_id,
)
from tests.helper_scripts.DynamicMagicMock import DynamicMagicMock


PATCH_ROOT = "middleware.primary_resource_logic.login_queries"


def test_generate_api_key():
    api_key = generate_api_key()
    assert len(api_key) == 32
    assert all(c in "0123456789abcdef" for c in api_key)


class GetAPIKeyForUserMocks(DynamicMagicMock):
    check_password_hash: MagicMock
    generate_api_key: MagicMock
    make_response: MagicMock


def setup_get_api_for_user_mocks():
    mock = GetAPIKeyForUserMocks(
        patch_root=PATCH_ROOT,
    )

    mock.db_client.get_user_info.return_value = DatabaseClient.UserInfo(
        id=mock.user_id,
        password_digest=mock.password_digest,
        api_key=None,
        email=mock.email,
    )
    mock.generate_api_key.return_value = mock.api_key
    return mock


def test_get_api_key_for_user_success(monkeypatch):
    mock = setup_get_api_for_user_mocks()
    mock.check_password_hash.return_value = True
    mock.generate_api_key.return_value = mock.api_key

    # Call function
    get_api_key_for_user(mock.db_client, mock.dto)

    assert_get_api_key_for_user_precondition_calls(mock)

    mock.generate_api_key.assert_called()
    mock.db_client.update_user_api_key.assert_called_with(
        user_id=mock.user_id, api_key=mock.api_key
    )
    mock.make_response.assert_called_with({"api_key": mock.api_key}, HTTPStatus.OK)


def test_get_api_key_for_user_failure():
    mock = setup_get_api_for_user_mocks()

    mock.check_password_hash.return_value = False

    get_api_key_for_user(mock.db_client, mock.dto)

    assert_get_api_key_for_user_precondition_calls(mock)

    mock.generate_api_key.assert_not_called()
    mock.db_client.update_user_api_key.assert_not_called()
    mock.make_response.assert_called_with(
        {"message": "Invalid email or password"}, HTTPStatus.UNAUTHORIZED
    )


def assert_get_api_key_for_user_precondition_calls(mock: GetAPIKeyForUserMocks):
    mock.db_client.get_user_info.assert_called_with(mock.dto.email)
    mock.check_password_hash.assert_called_with(mock.password_digest, mock.dto.password)


class RefreshSessionMocks(DynamicMagicMock):
    make_response: MagicMock
    create_session_token: MagicMock


@pytest.fixture
def setup_refresh_session_mocks():
    mock = RefreshSessionMocks(
        patch_root=PATCH_ROOT,
    )
    mock.db_client.get_session_token_info.return_value = mock.session_token_info
    mock.create_session_token.return_value = mock.new_token
    mock.session_token_info.resource_id = mock.mock_user_id
    mock.session_token_info.email = mock.mock_email

    return mock


class TryLoggingInWithGithubIdMocks(DynamicMagicMock):
    unauthorized_response: MagicMock
    login_response: MagicMock


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
        patch_root=PATCH_ROOT,
        return_values={
            "unauthorized_response": MagicMock(spec=Response),
            "login_response": MagicMock(spec=Response),
        },
    )

    mock.github_user_info.user_id = mock.github_user_id
    return mock


def test_try_logging_in_with_github_id_happy_path(
    setup_try_logging_in_with_github_id_mocks,
):
    mock = setup_try_logging_in_with_github_id_mocks

    mock.db_client.get_user_info_by_external_account_id.return_value = mock.user_info

    result = try_logging_in_with_github_id(mock.db_client, mock.github_user_info)

    assert_try_logging_in_with_github_id_precondition_calls(mock)

    assert result == mock.login_response.return_value
    mock.login_response.assert_called_once_with(mock.user_info)


def test_try_logging_in_with_github_id_unauthorized(
    setup_try_logging_in_with_github_id_mocks,
):
    mock = setup_try_logging_in_with_github_id_mocks

    mock.db_client.get_user_info_by_external_account_id.return_value = None

    result = try_logging_in_with_github_id(mock.db_client, mock.github_user_info)

    assert_try_logging_in_with_github_id_precondition_calls(mock)

    assert result == mock.unauthorized_response.return_value
    mock.unauthorized_response.assert_called_once()


class RefreshSessionMocks(DynamicMagicMock):
    get_jwt_identity: MagicMock
    create_access_token: MagicMock
    make_response: MagicMock


def test_refresh_session():
    mock = RefreshSessionMocks(
        patch_root=PATCH_ROOT,
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
