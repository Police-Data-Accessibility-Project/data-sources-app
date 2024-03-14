import jwt
import os
import datetime
from typing import Any, Dict, Union


def login_results(cursor, email: str) -> Dict[str, Union[int, str]]:
    """
    Query user data by email.

    Parameters:
    - cursor: Database cursor to execute the query.
    - email: User's email.

    Returns:
    - A dictionary containing user data if found, else returns a dictionary with an error message.
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


def is_admin(cursor, email):
    cursor.execute(f"select role from users where email = '{email}'")
    results = cursor.fetchall()
    if len(results) > 0:
        role = results[0][0]
        if role == "admin":
            return True
        return False

    else:
        return {"error": "no match"}


def create_session_token(cursor, id: int, email: str) -> str:
    """
    Create a session token for a user.

    Parameters:
    - cursor: Database cursor to execute the query.
    - id: User's ID.
    - email: User's email.

    Returns:
    - A session token.
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


def token_results(cursor, token):
    cursor.execute(f"select id, email from session_tokens where token = '{token}'")
def token_results(cursor, token: str) -> Dict[str, Union[int, str]]:
    """
    Query user data by session token.

    Parameters:
    - cursor: Database cursor to execute the query.
    - token: Session token.

    Returns:
    - A dictionary containing user data if found, else returns a dictionary with an error message.
    """
    results = cursor.fetchall()
    if len(results) > 0:
        user_data = {
            "id": results[0][0],
            "email": results[0][1],
        }
        return user_data
    else:
        return {"error": "no match"}
