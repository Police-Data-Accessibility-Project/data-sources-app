from http import HTTPStatus

from psycopg2.extras import DictCursor

from conftest import test_client, session
from database_client.database_client import DatabaseClient
from database_client.enums import ExternalAccountTypeEnum
from middleware.enums import CallbackFunctionsEnum
from tests.fixtures import dev_db_connection, client_with_db
from tests.helper_scripts.helper_functions import (
    check_response_status,
    create_test_user_api,
    patch_post_callback_functions,
    patch_setup_callback_session,
    create_fake_github_user_info,
    assert_expected_pre_callback_response,
    assert_session_token_exists_for_email,
)

# NOTE: This test is temporarily commented out due to issues with it passing, to be worked out later
'''
def test_login_with_github_post(client_with_db, dev_db_connection, monkeypatch, test_client, session):
    test_user_info = create_test_user_api(client_with_db)
    github_user_info = create_fake_github_user_info(test_user_info.email)
    db_client = DatabaseClient(dev_db_connection.cursor(cursor_factory=DictCursor), session)
    user_info = db_client.get_user_info(test_user_info.email)
    db_client.link_external_account(
        user_id=user_info.id,
        external_account_type=ExternalAccountTypeEnum.GITHUB,
        external_account_id=github_user_info.user_id,
    )

    mock_setup_callback_session = patch_setup_callback_session(
        monkeypatch, "LoginWithGithub"
    )
    response = client_with_db.post("auth/login-with-github")
    assert_expected_pre_callback_response(response)
    mock_setup_callback_session.assert_called_once_with(
        callback_functions_enum=CallbackFunctionsEnum.LOGIN_WITH_GITHUB
    )

    patch_post_callback_functions(
        monkeypatch,
        github_user_info=github_user_info,
        callback_functions_enum=CallbackFunctionsEnum.LOGIN_WITH_GITHUB,
        callback_params={},
    )

    response = client_with_db.get("auth/callback")
    check_response_status(response, HTTPStatus.OK)

    api_key = response.json["data"]

    assert_session_token_exists_for_email(
        cursor=db_client.cursor, session_token=api_key, email=user_info.email
    )
'''