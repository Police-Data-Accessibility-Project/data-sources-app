from http import HTTPStatus
from typing import Optional
from unittest.mock import MagicMock

import pytest
from flask import Response

from database_client.enums import ExternalAccountTypeEnum
from middleware.callback_primary_logic import (
    get_flask_session_callback_info,
    get_oauth_callback_info,
    callback_outer_wrapper,
    create_user_with_github,
    callback_inner_wrapper,
    link_github_account_request,
    link_github_account,
    get_github_user_info,
)
from middleware.dataclasses import (
    FlaskSessionCallbackInfo,
    OAuthCallbackInfo,
    GithubUserInfo,
)
from middleware.enums import CallbackFunctionsEnum
from tests.helper_scripts.DymamicMagicMock import DynamicMagicMock

PATCH_PREFIX = "middleware.callback_primary_logic"


class GetFlaskSessionCallbackInfoMocks(DynamicMagicMock):
    get_callback_params: MagicMock
    get_callback_function: MagicMock


def test_get_flask_session_callback_info():
    mock = GetFlaskSessionCallbackInfoMocks(
        patch_root=PATCH_PREFIX,
        mocks_to_patch=["get_callback_params", "get_callback_function"],
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


def test_get_oauth_callback_info():
    mock = GetOauthCallbackInfoMocks(
        patch_root=PATCH_PREFIX,
        mocks_to_patch=["get_github_user_info", "get_github_oauth_access_token"],
        return_values={
            "get_github_user_info": MagicMock(),
            "get_github_oauth_access_token": MagicMock(),
        },
    )

    result = get_oauth_callback_info()
    mock.get_github_oauth_access_token.assert_called_once()
    mock.get_github_user_info.assert_called_once_with(
        mock.get_github_oauth_access_token.return_value
    )

    assert isinstance(result, OAuthCallbackInfo)

    assert result.github_user_info == mock.get_github_user_info.return_value


class CallbackOuterWrapperMocks(DynamicMagicMock):
    db_client: MagicMock
    callback_inner_wrapper: MagicMock
    get_oauth_callback_info: MagicMock
    get_flask_session_callback_info: MagicMock


def test_callback_outer_wrapper():

    mock = CallbackOuterWrapperMocks(
        patch_root=PATCH_PREFIX,
        mocks_to_patch=[
            "callback_inner_wrapper",
            "get_oauth_callback_info",
            "get_flask_session_callback_info",
        ],
        return_values={
            "callback_inner_wrapper": MagicMock(spec=Response),
            "get_oauth_callback_info": OAuthCallbackInfo(
                github_user_info=MagicMock(spec=GithubUserInfo)
            ),
            "get_flask_session_callback_info": FlaskSessionCallbackInfo(
                callback_functions_enum=MagicMock(spec=CallbackFunctionsEnum),
                callback_params=MagicMock(spec=dict),
            ),
        },
    )

    result = callback_outer_wrapper(mock.db_client)

    mock.get_oauth_callback_info.assert_called_once()
    mock.get_flask_session_callback_info.assert_called_once()
    mock.callback_inner_wrapper.assert_called_once_with(
        db_client=mock.db_client,
        callback_function_enum=mock.get_flask_session_callback_info.return_value.callback_functions_enum,
        github_user_info=mock.get_oauth_callback_info.return_value.github_user_info,
        callback_params=mock.get_flask_session_callback_info.return_value.callback_params,
    )

    assert isinstance(result, Response)


class CreateUserWithGithubMocks(DynamicMagicMock):
    db_client: MagicMock
    github_user_info: MagicMock
    user_post_results: MagicMock
    create_random_password: MagicMock
    link_github_account: MagicMock
    make_response: MagicMock


def test_create_user_with_github():

    mock = CreateUserWithGithubMocks(
        patch_root=PATCH_PREFIX,
        mocks_to_patch=[
            "user_post_results",
            "create_random_password",
            "link_github_account",
            "make_response",
        ],
        return_values={
            "create_random_password": MagicMock(),
            "make_response": MagicMock(spec=Response),
        },
    )

    result = create_user_with_github(
        db_client=mock.db_client, github_user_info=mock.github_user_info
    )
    assert isinstance(result, Response)

    mock.user_post_results.assert_called_once_with(
        db_client=mock.db_client,
        email=mock.github_user_info.user_email,
        password=mock.create_random_password.return_value,
    )

    mock.link_github_account.assert_called_once_with(
        db_client=mock.db_client,
        github_user_info=mock.github_user_info,
        pdap_account_email=mock.github_user_info.user_email,
    )

    mock.make_response.assert_called_once_with(
        {"message": "Successfully created user account with linked Github account"},
        HTTPStatus.OK,
    )


class CallbackInnerWrapperMocks(DynamicMagicMock):
    db_client: MagicMock
    github_user_info: MagicMock
    callback_params: MagicMock
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
        mocks_to_patch=[
            "try_logging_in_with_github_id",
            "create_user_with_github",
            "link_github_account_request",
        ],
        return_values={
            "try_logging_in_with_github_id": MagicMock(spec=Response),
            "create_user_with_github": MagicMock(spec=Response),
            "link_github_account_request": MagicMock(spec=Response),
        },
    )
    return mock

def run_and_validate_callback_inner_wrapper_with_mocks(
    mock: CallbackInnerWrapperMocks,
    callback_function_enum: CallbackFunctionsEnum,
    check_is_response: bool = True
):
    result = callback_inner_wrapper(
        db_client=mock.db_client,
        callback_function_enum=callback_function_enum,
        github_user_info=mock.github_user_info,
        callback_params=mock.callback_params,
    )
    if check_is_response:
        assert isinstance(result, Response)


def test_callback_inner_wrapper_login_with_github(setup_callback_inner_wrapper_mocks):

    mock = setup_callback_inner_wrapper_mocks

    run_and_validate_callback_inner_wrapper_with_mocks(
        mock=mock,
        callback_function_enum=CallbackFunctionsEnum.LOGIN_WITH_GITHUB,
    )

    assert_callback_inner_wrapper_function_calls(
        mock=mock,
        called_function="try_logging_in_with_github_id",
        db_client=mock.db_client,
        github_user_info=mock.github_user_info,
    )

def test_callback_inner_wrapper_create_user_with_github(
    setup_callback_inner_wrapper_mocks,
):

    mock = setup_callback_inner_wrapper_mocks

    run_and_validate_callback_inner_wrapper_with_mocks(
        mock=mock,
        callback_function_enum=CallbackFunctionsEnum.CREATE_USER_WITH_GITHUB,
    )

    assert_callback_inner_wrapper_function_calls(
        mock=mock,
        called_function="create_user_with_github",
        db_client=mock.db_client,
        github_user_info=mock.github_user_info,
    )


def test_callback_inner_wrapper_link_to_github(setup_callback_inner_wrapper_mocks):

    mock = setup_callback_inner_wrapper_mocks

    run_and_validate_callback_inner_wrapper_with_mocks(
        mock=mock,
        callback_function_enum=CallbackFunctionsEnum.LINK_TO_GITHUB,
    )

    assert_callback_inner_wrapper_function_calls(
        mock=mock,
        called_function="link_github_account_request",
        db_client=mock.db_client,
        github_user_info=mock.github_user_info,
        pdap_account_email=mock.callback_params["user_email"],
    )


def test_callback_inner_wrapper_invalid_callback_function_enum(
    setup_callback_inner_wrapper_mocks,
):
    mock = setup_callback_inner_wrapper_mocks

    with pytest.raises(ValueError):
        run_and_validate_callback_inner_wrapper_with_mocks(
            mock=mock,
            callback_function_enum=MagicMock(),
            check_is_response=False
        )

    assert_callback_inner_wrapper_function_calls(mock=mock, called_function=None)


class LinkGithubAccountRequestMocks(DynamicMagicMock):
    db_client: MagicMock
    github_user_info: MagicMock
    pdap_account_email: MagicMock
    link_github_account: MagicMock
    make_response: MagicMock



def test_link_github_account_request():

    mock = LinkGithubAccountRequestMocks(
        patch_root=PATCH_PREFIX,
        mocks_to_patch=["link_github_account", "make_response"],
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
    mock.make_response.assert_called_once_with(
        {"message": "Successfully linked Github account"}, HTTPStatus.OK
    )


class LinkGithubAccountMocks(DynamicMagicMock):
    db_client: MagicMock
    github_user_info: MagicMock
    db_client_user_info: MagicMock
    pdap_account_email: MagicMock
    link_github_account: MagicMock


def test_link_github_account():

    mock = LinkGithubAccountMocks(
        patch_root=PATCH_PREFIX, mocks_to_patch=["link_github_account"]
    )
    mock.github_user_info.user_email = mock.pdap_account_email
    mock.db_client.get_user_info.return_value = mock.db_client_user_info
    mock.db_client_user_info.id = MagicMock()

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


class GetGithubUserInfoMocks(DynamicMagicMock):
    get_github_user_id: MagicMock
    get_github_user_email: MagicMock


def test_get_github_user_info():

    mock = GetGithubUserInfoMocks(
        patch_root=PATCH_PREFIX,
        mocks_to_patch=["get_github_user_id", "get_github_user_email"],
        return_values={
            "get_github_user_id": MagicMock(),
            "get_github_user_email": MagicMock(),
        },
    )

    result = get_github_user_info(access_token=mock.access_token)

    assert isinstance(result, GithubUserInfo)

    mock.get_github_user_id.assert_called_once_with(mock.access_token)
    mock.get_github_user_email.assert_called_once_with(mock.access_token)

    assert result.user_email == mock.get_github_user_email.return_value
    assert result.user_id == mock.get_github_user_id.return_value
