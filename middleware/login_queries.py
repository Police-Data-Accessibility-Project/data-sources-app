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

from middleware.custom_exceptions import UserNotFoundError, TokenNotFoundError


def get_user_info(cursor: PgCursor, email: str) -> Dict[str, Union[int, str]]:
    """
    Retrieves user data by email.

    :param cursor: A cursor object from a psycopg2 connection.
    :param email: User's email.
    :return: A dictionary containing user data or an error message.
    """
    cursor.execute(
        f"select id, password_digest, api_key from users where email = %s", (email,)
    )
    results = cursor.fetchall()
    if len(results) == 0:
        raise UserNotFoundError(email)
    return {
        "id": results[0][0],
        "password_digest": results[0][1],
        "api_key": results[0][2],
    }


def try_logging_in(cursor: PgCursor, email: str, password: str) -> Response:
    """
    Tries to log in a user.

    :param cursor: A cursor object from a psycopg2 connection.
    :param email: User's email.
    :param password: User's password.
    :return: A response object with a message and status code.
    """
    user_info = get_user_info(cursor, email)
    if check_password_hash(user_info["password_digest"], password):
        token = create_session_token(cursor, user_info["id"], email)
        return make_response(
            {"message": "Successfully logged in", "data": token}, HTTPStatus.OK
        )
    return make_response(
        {"message": "Invalid email or password"}, HTTPStatus.UNAUTHORIZED
    )


def is_admin(cursor: PgCursor, email: str) -> bool:
    """
    Checks if a user has an admin role.

    :param cursor: A cursor object from a psycopg2 connection.
    :param email: User's email.
    :return: True if user is an admin, False if not, or an error message.
    """
    cursor.execute(f"select role from users where email = %s", (email,))
    results = cursor.fetchall()
    try:
        role = results[0][0]
        if role == "admin":
            return True
        return False
    except IndexError:
        raise UserNotFoundError(email)


def create_session_token(cursor: PgCursor, user_id: int, email: str) -> str:
    """
    Generates a session token for a user and inserts it into the session_tokens table.

    :param cursor: A cursor object from a psycopg2 connection.
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
    session_token = jwt.encode(payload, os.getenv("SECRET_KEY"), algorithm="HS256")
    cursor.execute(
        f"insert into session_tokens (token, email, expiration_date) values (%s, %s, %s)",
        (session_token, email, expiration),
    )

    return session_token


SessionTokenUserData = namedtuple("SessionTokenUserData", ["id", "email"])


def get_session_token_user_data(cursor: PgCursor, token: str) -> SessionTokenUserData:
    """
    Retrieves session token data.

    :param cursor: A cursor object from a psycopg2 connection.
    :param token: The session token.
    :return: Session token data or an error message.
    """
    cursor.execute(f"select id, email from session_tokens where token = %s", (token,))
    results = cursor.fetchall()
    if len(results) == 0:
        raise TokenNotFoundError("The specified token was not found.")
    return SessionTokenUserData(id=results[0][0], email=results[0][1])


def delete_session_token(cursor, old_token):
    cursor.execute(f"delete from session_tokens where token = '{old_token}'")


def generate_api_key() -> str:
    return uuid.uuid4().hex


def get_api_key_for_user(cursor: PgCursor, email: str, password: str) -> Response:
    """
    Tries to log in a user. If successful, generates API key

    :param cursor: A cursor object from a psycopg2 connection.
    :param email: User's email.
    :param password: User's password.
    :return: A response object with a message and status code.
    """
    user_data = get_user_info(cursor, email)

    if check_password_hash(user_data["password_digest"], password):
        api_key = generate_api_key()
        user_id = str(user_data["id"])
        update_api_key(cursor, api_key, user_id)
        payload = {"api_key": api_key}
        return make_response(payload, HTTPStatus.OK)

    return make_response(
        {"message": "Invalid email or password"}, HTTPStatus.UNAUTHORIZED
    )


def update_api_key(cursor, api_key, user_id):
    cursor.execute("UPDATE users SET api_key = %s WHERE id = %s", (api_key, user_id))


def refresh_session(cursor: PgCursor, old_token: str) -> Response:
    try:
        user_data = get_session_token_user_data(cursor, old_token)
    except TokenNotFoundError:
        return make_response({"message": "Invalid session token"}, HTTPStatus.FORBIDDEN)
    delete_session_token(cursor, old_token)
    token = create_session_token(cursor, user_data.id, user_data.email)
    return make_response(
        {"message": "Successfully refreshed session token", "data": token},
        HTTPStatus.OK
    )
