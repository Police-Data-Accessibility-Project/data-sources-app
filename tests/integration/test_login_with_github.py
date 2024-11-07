from http import HTTPStatus

from database_client.database_client import DatabaseClient
from database_client.enums import ExternalAccountTypeEnum
from middleware.enums import CallbackFunctionsEnum
from middleware.schema_and_dto_logic.common_response_schemas import MessageSchema
from resources.endpoint_schema_config import SchemaConfigs
from tests.conftest import dev_db_client, flask_client_with_db
from tests.helper_scripts.helper_functions import (
    create_test_user_api,
    patch_post_callback_functions,
    patch_setup_callback_session,
    create_fake_github_user_info,
)
from tests.helper_scripts.common_test_functions import (
    assert_expected_pre_callback_response,
    assert_api_key_exists_for_email,
    assert_jwt_token_matches_user_email,
)
from tests.helper_scripts.run_and_validate_request import run_and_validate_request
from tests.helper_scripts.simple_result_validators import check_response_status


def test_login_with_github_get_pre_callback(
    flask_client_with_db, dev_db_client, monkeypatch
):

    # Setup Callback Session Mock for the LoginWithGithub module
    mock_setup_callback_session = patch_setup_callback_session(
        monkeypatch, "LoginWithGithub"
    )
    # Call the LoginWithGithub endpoint
    response = flask_client_with_db.get("auth/login-with-github")

    # Assert the correct pre_callback response was returned
    # And the proper callback session was set up
    assert_expected_pre_callback_response(response)
    mock_setup_callback_session.assert_called_once_with(
        callback_functions_enum=CallbackFunctionsEnum.LOGIN_WITH_GITHUB
    )


def test_login_with_github_get_post_callback_happy_path(
    flask_client_with_db, dev_db_client, monkeypatch
):
    test_user_info = create_test_user_api(flask_client_with_db)
    github_user_info = create_fake_github_user_info(test_user_info.email)
    user_info = dev_db_client.get_user_info(test_user_info.email)

    # Create a mock external account to GitHub for the user
    dev_db_client.link_external_account(
        user_id=user_info.id,
        external_account_type=ExternalAccountTypeEnum.GITHUB,
        external_account_id=github_user_info.user_id,
    )

    # Now, setup the post-callback function to emulate the session
    # having been set up properly
    patch_post_callback_functions(
        monkeypatch,
        github_user_info=github_user_info,
        callback_functions_enum=CallbackFunctionsEnum.LOGIN_WITH_GITHUB,
        callback_params={},
    )

    # Call the callback function and assert an access token was returned.
    # and that the JWT token matches the user's email
    response_json = run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="get",
        endpoint="auth/callback",
        expected_schema=SchemaConfigs.AUTH_GITHUB_LOGIN.value.primary_output_schema,
    )

    access_token = response_json["access_token"]

    assert_jwt_token_matches_user_email(
        email=user_info.email,
        jwt_token=access_token,
    )


def test_login_with_github_get_post_callback_no_pdap_user(
    flask_client_with_db, dev_db_client, monkeypatch
):
    """
    If a Github user account exists but no PDAP user is found,
    create that PDAP user and link them to the Github user account
    :param flask_client_with_db:
    :param dev_db_client:
    :param monkeypatch:
    :return:
    """

    github_user_info = create_fake_github_user_info()

    # Do NOT Create a mock external account to GitHub for the user in the DB

    # Now, setup the post-callback function to emulate the session
    # having been set up properly
    patch_post_callback_functions(
        monkeypatch,
        github_user_info=github_user_info,
        callback_functions_enum=CallbackFunctionsEnum.LOGIN_WITH_GITHUB,
        callback_params={},
    )

    # Call the callback function and check that a user is created
    response_json = run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="get",
        endpoint="auth/callback",
        expected_schema=SchemaConfigs.AUTH_GITHUB_LOGIN.value.primary_output_schema,
    )

    message = response_json["message"]
    message == f"User with email {github_user_info.user_email} created and logged in."

    # Check in the database that the user exists
    user_info = dev_db_client.get_user_info(email=github_user_info.user_email)
    assert user_info is not None

    # Check in the database that the Github account is linked to the new user
    user_info_gh = dev_db_client.get_user_info_by_external_account_id(
        external_account_id=str(github_user_info.user_id),
        external_account_type=ExternalAccountTypeEnum.GITHUB,
    )
    assert user_info_gh == user_info


def test_login_with_github_get_post_callback_accounts_exist_but_unlinked(
    flask_client_with_db, dev_db_client, monkeypatch
):
    """
    If a PDAP user exists and a Github account exists with that email
    But is not linked to that PDAP account,
    throw an error and indicate to the user to link their accounts

    """
    # Create a PDAP and fake Github user with same email, but do not link them
    test_user_info = create_test_user_api(flask_client_with_db)
    github_user_info = create_fake_github_user_info(email=test_user_info.email)

    # Now, setup the post-callback function to emulate the session
    # having been set up properly
    patch_post_callback_functions(
        monkeypatch,
        github_user_info=github_user_info,
        callback_functions_enum=CallbackFunctionsEnum.LOGIN_WITH_GITHUB,
        callback_params={},
    )

    # Call the callback function and check that no user is found
    response_json = run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="get",
        endpoint="auth/callback",
        expected_schema=MessageSchema,
        expected_response_status=HTTPStatus.UNAUTHORIZED,
    )

    message = response_json["message"]
    message == (
        f"User with email {github_user_info.user_email} exists but is not linked to the Github Account with the same email. "
        f"You must explicitly link their accounts in order to log in via Github."
    )
