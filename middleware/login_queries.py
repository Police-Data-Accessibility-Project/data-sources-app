import uuid
from collections import namedtuple
from datetime import datetime as dt
from http import HTTPStatus

import jwt
import os
import datetime
from typing import Union, Dict

from flask import Response, make_response
from psycopg2.extensions import cursor as PgCursor
from werkzeug.security import check_password_hash

from database_client.database_client import DatabaseClient
from middleware.custom_exceptions import UserNotFoundError, TokenNotFoundError
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
    if check_password_hash(user_info.password_digest, password):
        token = create_session_token(db_client, user_info.id, email)
        return make_response(
            {"message": "Successfully logged in", "data": token}, HTTPStatus.OK
        )
    return make_response(
        {"message": "Invalid email or password"}, HTTPStatus.UNAUTHORIZED
    )


def is_admin(db_client: DatabaseClient, email: str) -> bool:
    """
    Checks if a user has an admin role.

    :param cursor: A cursor object from a psycopg2 connection.
    :param email: User's email.
    :return: True if user is an admin, False if not, or an error message.
    """
    role_info = db_client.get_role_by_email(email)
    return role_info.role == "admin"

def create_session_token(db_client: DatabaseClient, user_id: int, email: str) -> str:
    """
    Generates a session token for a user and inserts it into the session_tokens table.

    :param db_client: A DatabaseClient object.
    :param user_id: The user's ID.
    :param email: User's email.
    :return: A session token.
    """
    expiration = datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=300)
    payload = {
        "exp": expiration,
        "iat": datetime.datetime.utcnow(),
        "sub": user_id,
    }
    session_token = jwt.encode(
        payload, get_env_variable("SECRET_KEY"), algorithm="HS256"
    )
    db_client.add_new_session_token(
        session_token=session_token, email=email, expiration=expiration
    )

    return session_token


SessionTokenUserData = namedtuple("SessionTokenUserData", ["id", "email"])

def generate_api_key() -> str:
    return uuid.uuid4().hex


def get_api_key_for_user(db_client: DatabaseClient, email: str, password: str) -> Response:
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
        db_client.update_user_api_key(
            user_id=user_data.id, api_key=api_key
        )
        payload = {"api_key": api_key}
        return make_response(payload, HTTPStatus.OK)

    return make_response(
        {"message": "Invalid email or password"}, HTTPStatus.UNAUTHORIZED
    )


def refresh_session(db_client: DatabaseClient, old_token: str) -> Response:
    try:
        user_info = db_client.get_user_info_by_session_token(old_token)
    except TokenNotFoundError:
        return make_response({"message": "Invalid session token"}, HTTPStatus.FORBIDDEN)
    db_client.delete_session_token(old_token)
    token = create_session_token(db_client, user_info.id, user_info.email)
    return make_response(
        {"message": "Successfully refreshed session token", "data": token},
        HTTPStatus.OK,
    )
