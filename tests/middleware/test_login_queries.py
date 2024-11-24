from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from flask import Response

from database_client.enums import ExternalAccountTypeEnum
from middleware.primary_resource_logic.login_queries import (
    refresh_session,
)
from middleware.primary_resource_logic.api_key_logic import generate_token
from tests.helper_scripts.DynamicMagicMock import DynamicMagicMock


PATCH_ROOT = "middleware.primary_resource_logic.login_queries"


def test_generate_api_key():
    api_key = generate_token()
    assert len(api_key) == 32
    assert all(c in "0123456789abcdef" for c in api_key)


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
