from http import HTTPStatus

from database_client.database_client import DatabaseClient
from database_client.enums import ExternalAccountTypeEnum
from middleware.enums import CallbackFunctionsEnum
from tests.fixtures import dev_db_connection, flask_client_with_db, dev_db_client
from tests.helper_scripts.helper_functions import (
    create_test_user_api,
    patch_post_callback_functions,
    patch_setup_callback_session,
    create_fake_github_user_info,
)
from tests.helper_scripts.common_test_functions import assert_expected_pre_callback_response, \
    assert_api_key_exists_for_email, assert_jwt_token_matches_user_email
from tests.helper_scripts.run_and_validate_request import run_and_validate_request
from tests.helper_scripts.simple_result_validators import check_response_status


def test_login_with_github_post(flask_client_with_db, dev_db_client, monkeypatch):
    test_user_info = create_test_user_api(flask_client_with_db)
    github_user_info = create_fake_github_user_info(test_user_info.email)
    user_info = dev_db_client.get_user_info(test_user_info.email)
    dev_db_client.link_external_account(
        user_id=user_info.id,
        external_account_type=ExternalAccountTypeEnum.GITHUB,
        external_account_id=github_user_info.user_id,
    )

    mock_setup_callback_session = patch_setup_callback_session(
        monkeypatch, "LoginWithGithub"
    )
    response = flask_client_with_db.post("auth/login-with-github")
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

    response_json = run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="get",
        endpoint="auth/callback",
    )

    access_token = response_json["access_token"]

    assert_jwt_token_matches_user_email(
        email=user_info.email,
        jwt_token=access_token,
    )
