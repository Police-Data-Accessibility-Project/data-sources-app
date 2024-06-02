from collections import namedtuple
from datetime import datetime as dt

import jwt
import os
import datetime
from typing import Union, Dict
from psycopg2.extensions import cursor as PgCursor

from middleware.custom_exceptions import UserNotFoundError, TokenNotFoundError


def login_results(cursor: PgCursor, email: str) -> Dict[str, Union[int, str]]:
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
