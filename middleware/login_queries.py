import uuid
from collections import namedtuple
from http import HTTPStatus

import jwt
import datetime

from flask import Response, make_response, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, create_refresh_token
from werkzeug.security import check_password_hash

from database_client.database_client import DatabaseClient
from database_client.enums import ExternalAccountTypeEnum
from middleware.dataclasses import GithubUserInfo
from middleware.util import get_env_variable


def try_logging_in(db_client: DatabaseClient, email: str, password: str) -> Response:
    """
    Tries to log in a user.

    :param db_client: DatabaseClient object.
    :param email: User's email.
    :param password: User's password.
    :return: A response object with a message and status code.
    """
    user_info = db_client.get_user_info(email)
    if not check_password_hash(user_info.password_digest, password):
        return unauthorized_response("Invalid email or password")
    return login_response(user_info)


def try_logging_in_with_github_id(
        db_client: DatabaseClient,
        github_user_info: GithubUserInfo
) -> Response:
    """
    Tries to log in a user.

    :param github_user_info: GithubUserInfo object.
    :param db_client: DatabaseClient object.
    :return: A response object with a message and status code.
    """
    user_info = db_client.get_user_info_by_external_account_id(
        external_account_id=github_user_info.user_id,
        external_account_type=ExternalAccountTypeEnum.GITHUB
    )
    if not user_info:
        return unauthorized_response("Github user not found")
    return login_response(user_info)

def unauthorized_response(msg: str = "Unauthorized") -> Response:
    """
    Creates a response object for an unauthorized request.

    :return: A response object with a message and status code.
    """
    return make_response({"message": msg}, HTTPStatus.UNAUTHORIZED)

def login_response(
        user_info: DatabaseClient.UserInfo) -> Response:
    """
    Creates a response object for a successful login.

    :param user_info: The user's information.
    :return: A response object with a message and status code.
    """
    access_token = create_access_token(identity=user_info.email)
    refresh_token = create_refresh_token(identity=user_info.email)
    return make_response(
        jsonify(
            message="Successfully logged in",
            access_token=access_token,
            refresh_token=refresh_token
        ), HTTPStatus.OK
    )

def generate_api_key() -> str:
    return uuid.uuid4().hex


def get_api_key_for_user(
    db_client: DatabaseClient, email: str, password: str
) -> Response:
    """
    Tries to log in a user. If successful, generates API key

    :param db_client: A DatabaseClient object.
    :param email: User's email.
    :param password: User's password.
    :return: A response object with a message and status code.
    """
    user_data = db_client.get_user_info(email)

    if check_password_hash(user_data.password_digest, password):
        api_key = generate_api_key()
        db_client.update_user_api_key(user_id=user_data.id, api_key=api_key)
        payload = {"api_key": api_key}
        return make_response(payload, HTTPStatus.OK)

    return make_response(
        {"message": "Invalid email or password"}, HTTPStatus.UNAUTHORIZED
    )


def refresh_session() -> Response:
    """
    Requires an active flask context and a valid JWT passed in the Authorization header
    :return:
    """
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return make_response(
        {"message": "Successfully refreshed session token", "data": access_token},
        HTTPStatus.OK,
    )
