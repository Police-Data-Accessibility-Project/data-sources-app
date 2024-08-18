from http import HTTPStatus

from psycopg2.extras import DictCursor

from database_client.database_client import DatabaseClient
from database_client.enums import ExternalAccountTypeEnum
from middleware.enums import CallbackFunctionsEnum
from tests.fixtures import dev_db_connection, flask_client_with_db
from tests.helper_scripts.helper_functions import (
    check_response_status,
    patch_post_callback_functions,
    patch_setup_callback_session,
    create_fake_github_user_info,
    assert_expected_pre_callback_response,
    run_and_validate_request,
)


def test_create_user_with_github_post(
    flask_client_with_db, dev_db_connection, monkeypatch
):

    github_user_info = create_fake_github_user_info()
    mock_setup_callback_session = patch_setup_callback_session(
        monkeypatch, "CreateUserWithGithub"
    )
    response = flask_client_with_db.post("auth/create-user-with-github")
    assert_expected_pre_callback_response(response)
    mock_setup_callback_session.assert_called_once_with(
        callback_functions_enum=CallbackFunctionsEnum.CREATE_USER_WITH_GITHUB
    )

    patch_post_callback_functions(
        monkeypatch,
        github_user_info=github_user_info,
        callback_functions_enum=CallbackFunctionsEnum.CREATE_USER_WITH_GITHUB,
        callback_params={},
    )

    run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="get",
        endpoint="auth/callback",
    )

    db_client = DatabaseClient()
    user_info = db_client.get_user_info_by_external_account_id(
        github_user_info.user_id, ExternalAccountTypeEnum.GITHUB
    )
    db_client.close()

    assert user_info is not None
    assert user_info.email == github_user_info.user_email
