from http import HTTPStatus

import psycopg

from middleware.enums import CallbackFunctionsEnum
from tests.fixtures import dev_db_connection, flask_client_with_db
from tests.helper_scripts.helper_functions import (
    create_test_user_api,
    create_api_key,
    patch_post_callback_functions,
    patch_setup_callback_session,
    create_fake_github_user_info,
    create_test_user_setup,
)
from tests.helper_scripts.common_test_functions import check_response_status, assert_expected_pre_callback_response, \
    run_and_validate_request


def test_link_to_github(
    flask_client_with_db, dev_db_connection: psycopg.Connection, monkeypatch
):
    tus = create_test_user_setup(flask_client_with_db)
    mock_setup_callback_session = patch_setup_callback_session(
        monkeypatch, "LinkToGithub"
    )
    mock_params = {
        "redirect_to": "test_page",
        "user_email": tus.user_info.email,
    }
    response = flask_client_with_db.post(
        "auth/link-to-github",
        headers=tus.api_authorization_header,
        json=mock_params,
    )
    assert_expected_pre_callback_response(response)

    mock_setup_callback_session.assert_called_once_with(
        callback_functions_enum=CallbackFunctionsEnum.LINK_TO_GITHUB,
        redirect_to="test_page",
        user_email=tus.user_info.email,
    )

    github_user_info = create_fake_github_user_info(tus.user_info.email)
    patch_post_callback_functions(
        monkeypatch,
        github_user_info=github_user_info,
        callback_functions_enum=CallbackFunctionsEnum.LINK_TO_GITHUB,
        callback_params=mock_params,
    )
    run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="get",
        endpoint="auth/callback",
    )

    cursor = dev_db_connection.cursor()
    cursor.execute(
        "SELECT account_type, account_identifier FROM user_external_accounts WHERE email = %s",
        (tus.user_info.email,),
    )
    result = cursor.fetchone()
    assert result == ("github", github_user_info.user_id)
