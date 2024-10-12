from http import HTTPStatus

import psycopg

from database_client.database_client import DatabaseClient
from middleware.enums import CallbackFunctionsEnum
from tests.conftest import flask_client_with_db
from tests.helper_scripts.helper_functions import (
    create_test_user_api,
    create_api_key,
    patch_post_callback_functions,
    patch_setup_callback_session,
    create_fake_github_user_info,
    create_test_user_setup,
)
from tests.helper_scripts.common_test_functions import (
    assert_expected_pre_callback_response,
)
from tests.helper_scripts.run_and_validate_request import run_and_validate_request
from tests.helper_scripts.simple_result_validators import check_response_status


def test_link_to_github(flask_client_with_db, monkeypatch):
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

    db_client = DatabaseClient()
    result = db_client.execute_raw_sql(
        query="SELECT account_type, account_identifier FROM user_external_accounts WHERE email = %s",
        vars=(tus.user_info.email,),
    )[0]
    assert result == {
        "account_identifier": github_user_info.user_id,
        "account_type": "github",
    }
