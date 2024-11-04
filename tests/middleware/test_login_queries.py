from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from flask import Response

from database_client.enums import ExternalAccountTypeEnum
from middleware.primary_resource_logic.login_queries import (
    refresh_session,
)
from middleware.primary_resource_logic.api_key_logic import generate_api_key
from tests.helper_scripts.DynamicMagicMock import DynamicMagicMock


PATCH_ROOT = "middleware.primary_resource_logic.login_queries"


def test_generate_api_key():
    api_key = generate_api_key()
    assert len(api_key) == 32
    assert all(c in "0123456789abcdef" for c in api_key)


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
