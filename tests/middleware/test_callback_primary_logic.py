from http import HTTPStatus
from typing import Optional
from unittest.mock import MagicMock

import pytest
from flask import Response

from db.enums import ExternalAccountTypeEnum
from middleware.primary_resource_logic.callback import (
    get_flask_session_callback_info,
)
from middleware.primary_resource_logic.github_oauth import (
    link_github_account_request,
    link_github_account,
    get_github_user_info,
)
from middleware.custom_dataclasses import (
    FlaskSessionCallbackInfo,
    OAuthCallbackInfo,
    GithubUserInfo,
)
from tests.helper_scripts.DynamicMagicMock import DynamicMagicMock

PATCH_PREFIX = "middleware.primary_resource_logic.callback"
GITHUB_OAUTH_PREFIX = "middleware.primary_resource_logic.github_oauth"


class GetFlaskSessionCallbackInfoMocks(DynamicMagicMock):
    get_callback_params: MagicMock
    get_callback_function: MagicMock


def test_get_flask_session_callback_info():
    mock = GetFlaskSessionCallbackInfoMocks(
        patch_root=PATCH_PREFIX,
        return_values={
            "get_callback_params": MagicMock(),
            "get_callback_function": MagicMock(),
        },
    )

    result = get_flask_session_callback_info()
    mock.get_callback_params.assert_called_once()
    mock.get_callback_function.assert_called_once()

    assert isinstance(result, FlaskSessionCallbackInfo)

    assert result.callback_params == mock.get_callback_params.return_value
    assert result.callback_functions_enum == mock.get_callback_function.return_value


class GetOauthCallbackInfoMocks(DynamicMagicMock):
    get_github_user_info: MagicMock
    get_github_oauth_access_token: MagicMock


class CallbackInnerWrapperMocks(DynamicMagicMock):
    try_logging_in_with_github_id: MagicMock
    create_user_with_github: MagicMock
    link_github_account_request: MagicMock


def assert_callback_inner_wrapper_function_calls(
    mock: CallbackInnerWrapperMocks, called_function: Optional[str], **expected_kwargs
):
    for function_name in (
        "try_logging_in_with_github_id",
        "create_user_with_github",
        "link_github_account_request",
    ):
        if function_name == called_function:
            getattr(mock, function_name).assert_called_once_with(**expected_kwargs)
        else:
            getattr(mock, function_name).assert_not_called()


@pytest.fixture
def setup_callback_inner_wrapper_mocks():
    mock = CallbackInnerWrapperMocks(
        patch_root=PATCH_PREFIX,
        return_values={
            "try_logging_in_with_github_id": MagicMock(spec=Response),
            "create_user_with_github": MagicMock(spec=Response),
            "link_github_account_request": MagicMock(spec=Response),
        },
    )
    return mock


class LinkGithubAccountRequestMocks(DynamicMagicMock):
    link_github_account: MagicMock
    message_response: MagicMock


def test_link_github_account_request():

    mock = LinkGithubAccountRequestMocks(
        patch_root=GITHUB_OAUTH_PREFIX,
    )

    link_github_account_request(
        db_client=mock.db_client,
        github_user_info=mock.github_user_info,
        pdap_account_email=mock.pdap_account_email,
    )

    mock.link_github_account.assert_called_once_with(
        db_client=mock.db_client,
        github_user_info=mock.github_user_info,
        pdap_account_email=mock.pdap_account_email,
    )
    mock.message_response.assert_called_once_with("Successfully linked Github account")


class LinkGithubAccountMocks(DynamicMagicMock):
    link_github_account: MagicMock


def test_link_github_account():

    mock = LinkGithubAccountMocks(patch_root=GITHUB_OAUTH_PREFIX)
    mock.github_user_info.user_email = mock.pdap_account_email
    mock.db_client.get_user_info.return_value = mock.db_client_user_info

    link_github_account(
        db_client=mock.db_client,
        github_user_info=mock.github_user_info,
        pdap_account_email=mock.pdap_account_email,
    )

    mock.db_client.get_user_info.assert_called_once_with(email=mock.pdap_account_email)

    mock.db_client.link_external_account.assert_called_once_with(
        user_id=mock.db_client_user_info.id,
        external_account_id=mock.github_user_info.user_id,
        external_account_type=ExternalAccountTypeEnum.GITHUB,
    )
