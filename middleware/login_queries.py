import jwt
import os
import datetime
from typing import Union, Dict
from psycopg2.extensions import cursor as PgCursor


def login_results(
        cursor: PgCursor,
        email: str) \
        -> Dict[str, Union[int, str]]:
    """
    Retrieves user data by email.

    :param cursor: A cursor object from a psycopg2 connection.
    :param email: User's email.
    :return: A dictionary containing user data or an error message.
    """
    cursor.execute(
        f"select id, password_digest, api_key from users where email = '{email}'"
    )
    results = cursor.fetchall()
    if len(results) > 0:
        user_data = {
            "id": results[0][0],
            "password_digest": results[0][1],
            "api_key": results[0][2],
        }
        return user_data
    else:
        return {"error": "no match"}


def is_admin(
        cursor: PgCursor,
        email: str) \
        -> Union[bool, Dict[str, str]]:
    """
    Checks if a user has an admin role.

    :param cursor: A cursor object from a psycopg2 connection.
    :param email: User's email.
    :return: True if user is an admin, False if not, or an error message.
    """
    cursor.execute(f"select role from users where email = '{email}'")
    results = cursor.fetchall()
    if len(results) > 0:
        role = results[0][0]
        if role == "admin":
            return True
        return False

    else:
        return {"error": "no match"}


def create_session_token(
        cursor: PgCursor,
        user_id: int,
        email: str) \
        -> str:
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
        "sub": id,
    }
    session_token = jwt.encode(payload, os.getenv("SECRET_KEY"), algorithm="HS256")
    cursor.execute(
        f"insert into session_tokens (token, email, expiration_date) values ('{session_token}', '{email}', '{expiration}')"
    )

    return session_token


def token_results(
        cursor: PgCursor,
        token: str) \
        -> Dict[str, Union[int, str]]:
    """
    Retrieves session token data.

    :param cursor: A cursor object from a psycopg2 connection.
    :param token: The session token.
    :return: A dictionary containing session token data or an error message.
    """
    cursor.execute(f"select id, email from session_tokens where token = '{token}'")
    results = cursor.fetchall()
    if len(results) > 0:
        user_data = {
            "id": results[0][0],
            "email": results[0][1],
        }
        return user_data
    else:
        return {"error": "no match"}
