import uuid
from dataclasses import dataclass
from http import HTTPStatus

from flask import Response, make_response

from database_client.database_client import DatabaseClient
from database_client.enums import ExternalAccountTypeEnum
from middleware.common_response_formatting import message_response
from middleware.exceptions import UserNotFoundError
from middleware.flask_response_manager import FlaskResponseManager
from middleware.primary_resource_logic.login_queries import (
    unauthorized_response,
    login_response,
)
from middleware.third_party_interaction_logic.callback_flask_sessions_logic import (
    get_callback_params,
    get_callback_function,
)
from middleware.custom_dataclasses import (
    GithubUserInfo,
    FlaskSessionCallbackInfo,
    OAuthCallbackInfo,
)
from middleware.enums import CallbackFunctionsEnum
from middleware.third_party_interaction_logic.callback_oauth_logic import (
    get_github_user_id,
    get_github_user_email,
    get_github_oauth_access_token,
)
from middleware.primary_resource_logic.user_queries import (
    user_post_results,
    UserRequestDTO,
)


@dataclass
class LinkToGithubRequestDTO:
    redirect_to: str
    user_email: str


def get_flask_session_callback_info() -> FlaskSessionCallbackInfo:
    """
    Returns a FlaskSessionCallbackInfo object with the callback function and parameters
    :return:
    """
    return FlaskSessionCallbackInfo(
        callback_functions_enum=get_callback_function(),
        callback_params=get_callback_params(),
    )


def get_oauth_callback_info() -> OAuthCallbackInfo:
    """
    Returns a OAuthCallbackInfo object with the Github user information
    :return:
    """
    token = get_github_oauth_access_token()
    return OAuthCallbackInfo(github_user_info=get_github_user_info(token))


def callback_outer_wrapper(db_client: DatabaseClient) -> Response:
    """
    Outer wrapper for the callback function.
    This wrapper interfaces with the functions which interface with the Flask Sessions and OAuth2 logic
    and passes the results into the callback_inner_wrapper
    :param db_client:
    :return:
    """
    oauth_callback_info = get_oauth_callback_info()
    flask_session_callback_info = get_flask_session_callback_info()
    return callback_inner_wrapper(
        db_client=db_client,
        callback_function_enum=flask_session_callback_info.callback_functions_enum,
        github_user_info=oauth_callback_info.github_user_info,
        callback_params=flask_session_callback_info.callback_params,
    )


def create_random_password() -> str:
    return uuid.uuid4().hex


def create_user_with_github(
    db_client: DatabaseClient, github_user_info: GithubUserInfo
):
    user_post_results(
        db_client=db_client,
        dto=UserRequestDTO(
            email=github_user_info.user_email,
            # Create a random password. Will need to be reset if not logging in via Github
            password=create_random_password(),
        ),
    )
    link_github_account(
        db_client=db_client,
        github_user_info=github_user_info,
        pdap_account_email=github_user_info.user_email,
    )


def callback_inner_wrapper(
    db_client: DatabaseClient,
    callback_function_enum: CallbackFunctionsEnum,
    github_user_info: GithubUserInfo,
    callback_params: dict,
) -> Response:

    if callback_function_enum == CallbackFunctionsEnum.LOGIN_WITH_GITHUB:
        return try_logging_in_with_github_id(
            db_client=db_client, github_user_info=github_user_info
        )
    elif callback_function_enum == CallbackFunctionsEnum.LINK_TO_GITHUB:
        return link_github_account_request(
            db_client=db_client,
            github_user_info=github_user_info,
            pdap_account_email=callback_params["user_email"],
        )
    raise ValueError(f"Invalid callback function: {callback_function_enum}")


def link_github_account_request(
    db_client: DatabaseClient, github_user_info: GithubUserInfo, pdap_account_email: str
) -> Response:
    link_github_account(
        db_client=db_client,
        github_user_info=github_user_info,
        pdap_account_email=pdap_account_email,
    )
    return make_response(
        {"message": "Successfully linked Github account"}, HTTPStatus.OK
    )


def link_github_account(
    db_client: DatabaseClient, github_user_info: GithubUserInfo, pdap_account_email: str
):
    user_info = db_client.get_user_info(email=pdap_account_email)
    db_client.link_external_account(
        user_id=user_info.id,
        external_account_id=github_user_info.user_id,
        external_account_type=ExternalAccountTypeEnum.GITHUB,
    )


def get_github_user_info(access_token: str) -> GithubUserInfo:
    """
    Gets the user information from the Github API via OAuth2
    :param access_token: The access token from the Github API
    :return: The user information
    """
    return GithubUserInfo(
        user_id=get_github_user_id(access_token),
        user_email=get_github_user_email(access_token),
    )


def user_exists(db_client: DatabaseClient, email: str) -> bool:
    try:
        db_client.get_user_info(email=email)
        return True
    except UserNotFoundError:
        return False


def try_logging_in_with_github_id(
    db_client: DatabaseClient, github_user_info: GithubUserInfo
) -> Response:
    """
    Tries to log in a user.

    :param github_user_info: GithubUserInfo object.
    :param db_client: DatabaseClient object.
    :return: A response object with a message and status code.
    """
    try:
        user_info_gh = db_client.get_user_info_by_external_account_id(
            external_account_id=str(github_user_info.user_id),
            external_account_type=ExternalAccountTypeEnum.GITHUB,
        )
    except UserNotFoundError:
        # Check if user email exists
        if user_exists(db_client=db_client, email=github_user_info.user_email):
            return message_response(
                status_code=HTTPStatus.UNAUTHORIZED,
                message=f"User with email {github_user_info.user_email} already exists exists but is not linked to"
                f" the Github Account with the same email. You must explicitly link their accounts in order to log in via Github.",
            )

        create_user_with_github(db_client=db_client, github_user_info=github_user_info)
        user_info_gh = db_client.get_user_info_by_external_account_id(
            external_account_id=str(github_user_info.user_id),
            external_account_type=ExternalAccountTypeEnum.GITHUB,
        )

    return login_response(
        user_info_gh,
        message=f"User with email {user_info_gh.email} created and logged in.",
    )
