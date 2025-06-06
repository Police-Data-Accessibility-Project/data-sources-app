import uuid
from dataclasses import dataclass
from http import HTTPStatus

from flask import Response, make_response
from flask_restx import abort
from jwt import ExpiredSignatureError
from pydantic import BaseModel

from db.client import DatabaseClient
from db.enums import ExternalAccountTypeEnum
from middleware.SimpleJWT import SimpleJWT, JWTPurpose
from middleware.common_response_formatting import message_response
from middleware.custom_dataclasses import GithubUserInfo
from middleware.exceptions import UserNotFoundError
from middleware.primary_resource_logic.login_queries import login_response
from middleware.primary_resource_logic.user_queries import (
    user_post_results,
    UserRequestDTO,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.auth_schemas import (
    LoginWithGithubRequestDTO,
)
from middleware.third_party_interaction_logic.callback_oauth_logic import (
    get_github_user_id,
    get_github_user_email,
)


class LinkToGithubRequestDTO(BaseModel):
    gh_access_token: str
    user_email: str


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


def link_github_account_request_wrapper(
    db_client: DatabaseClient, dto: LinkToGithubRequestDTO
) -> Response:
    user_email = dto.user_email
    if not user_exists(db_client=db_client, email=user_email):
        return message_response(
            status_code=HTTPStatus.BAD_REQUEST,
            message="Email provided not associated with any user.",
        )
    github_user_info = get_github_user_info(access_token=dto.gh_access_token)
    if user_email != github_user_info.user_email:
        return message_response(
            status_code=HTTPStatus.BAD_REQUEST,
            message="Email provided does not match primary email in GitHub account.",
        )
    return link_github_account_request(
        db_client=db_client,
        github_user_info=github_user_info,
        pdap_account_email=dto.user_email,
    )


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
    try:
        simple_jwt = SimpleJWT.decode(
            access_token, expected_purpose=JWTPurpose.GITHUB_ACCESS_TOKEN
        )
    except ExpiredSignatureError:
        abort(HTTPStatus.UNAUTHORIZED, "Access token has expired.")
    gh_access_token = simple_jwt.sub
    return GithubUserInfo(
        user_id=get_github_user_id(gh_access_token),
        user_email=get_github_user_email(gh_access_token),
    )


def user_exists(db_client: DatabaseClient, email: str) -> bool:
    try:
        db_client.get_user_info(email=email)
        return True
    except UserNotFoundError:
        return False


def login_with_github_wrapper(
    db_client: DatabaseClient, dto: LoginWithGithubRequestDTO
):

    github_user_info = get_github_user_info(access_token=dto.gh_access_token)
    return try_logging_in_with_github_id(
        db_client=db_client, github_user_info=github_user_info
    )


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
