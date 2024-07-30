import datetime
import uuid
from http import HTTPStatus
import json
from unittest.mock import MagicMock

import psycopg2

from middleware.dataclasses import (
    OAuthCallbackInfo,
    GithubUserInfo,
    FlaskSessionCallbackInfo,
)
from middleware.enums import CallbackFunctionsEnum
from tests.fixtures import dev_db_connection, client_with_db
from tests.helper_functions import (
    check_response_status,
    create_test_user_api,
    create_api_key,
    assert_is_oauth_redirect_link,
    patch_post_callback_functions,
    patch_setup_callback_session,
    create_fake_github_user_info,
    assert_expected_pre_callback_response,
)


def test_link_to_github(
    client_with_db, dev_db_connection: psycopg2.extensions.connection, monkeypatch
):
    test_user_info = create_test_user_api(client_with_db)
    api_key = create_api_key(client_with_db, test_user_info)
    mock_setup_callback_session = patch_setup_callback_session(
        monkeypatch, "LinkToGithub"
    )
    mock_params = {
        "redirect_to": "test_page",
        "user_email": test_user_info.email,
    }
    response = client_with_db.post(
        "auth/link-to-github",
        headers={"Authorization": f"Bearer {api_key}"},
        json=mock_params,
    )
    assert_expected_pre_callback_response(response)

    mock_setup_callback_session.assert_called_once_with(
        callback_functions_enum=CallbackFunctionsEnum.LINK_TO_GITHUB,
        redirect_to="test_page",
        user_email=test_user_info.email,
    )

    github_user_info = create_fake_github_user_info(test_user_info.email)
    patch_post_callback_functions(
        monkeypatch,
        github_user_info=github_user_info,
        callback_functions_enum=CallbackFunctionsEnum.LINK_TO_GITHUB,
        callback_params=mock_params,
    )
    response = client_with_db.get("auth/callback")
    check_response_status(response, HTTPStatus.OK)
    cursor = dev_db_connection.cursor()
    cursor.execute(
        "SELECT account_type, account_identifier FROM user_external_accounts WHERE email = %s",
        (test_user_info.email,),
    )
    result = cursor.fetchone()
    assert result[0] == "github"
    assert result[1] == github_user_info.user_id
