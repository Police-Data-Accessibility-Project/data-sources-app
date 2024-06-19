import uuid
from datetime import datetime
from http import HTTPStatus

from flask import Response, make_response
from psycopg2.extensions import cursor as PgCursor
from typing import Dict, Union

from werkzeug.security import generate_password_hash

from middleware.custom_exceptions import TokenNotFoundError
from middleware.login_queries import generate_api_key
from middleware.user_queries import user_check_email
from middleware.webhook_logic import send_password_reset_link


class InvalidTokenError(Exception):
    pass


def check_reset_token(cursor: PgCursor, token: str) -> Dict[str, Union[int, str]]:
    """
    Checks if a reset token exists in the database and retrieves the associated user data.

    :param cursor: A cursor object from a psycopg2 connection.
    :param token: The reset token to check.
    :return: A dictionary containing the user's ID, token creation date, and email if the token exists; otherwise, an error message.
    """
    cursor.execute(
        f"select id, create_date, email from reset_tokens where token = %s", (token,)
    )
    results = cursor.fetchall()
    if len(results) == 0:
        raise TokenNotFoundError("The specified token was not found.")
    return {
        "id": results[0][0],
        "create_date": results[0][1],
        "email": results[0][2],
    }


def add_reset_token(cursor: PgCursor, email: str, token: str) -> None:
    """
    Inserts a new reset token into the database for a specified email.

    :param cursor: A cursor object from a psycopg2 connection.
    :param email: The email to associate with the reset token.
    :param token: The reset token to add.
    """
    cursor.execute(
        f"insert into reset_tokens (email, token) values (%s, %s)", (email, token)
    )

    return


def delete_reset_token(cursor: PgCursor, email: str, token: str) -> None:
    """
    Deletes a reset token from the database for a specified email.

    :param cursor: A cursor object from a psycopg2 connection.
    :param email: The email associated with the reset token to delete.
    :param token: The reset token to delete.
    """
    cursor.execute(
        f"delete from reset_tokens where email = %s and token = %s", (email, token)
    )

    return


def request_reset_password(cursor, email) -> Response:
    """
    Generates a reset token and sends an email to the user with instructions on how to reset their password.
    :param cursor:
    :param email:
    :return:
    """
    user_check_email(cursor, email)
    token = generate_api_key()
    add_reset_token(cursor, email, token)
    send_password_reset_link(email, token)
    return make_response(
        {
            "message": "An email has been sent to your email address with a link to reset your password. It will be valid for 15 minutes.",
            "token": token,
        },
        HTTPStatus.OK,
    )


def reset_password(cursor, token, password) -> Response:
    """
    Resets a user's password if the provided token is valid and not expired.
    :param cursor:
    :param token:
    :param password:
    :return:
    """
    try:
        email = validate_token(cursor, token)
    except InvalidTokenError:
        return invalid_token_response()
    set_user_password(cursor, email, password)
    return make_response({"message": "Successfully updated password"}, HTTPStatus.OK)


def set_user_password(cursor, email, password):
    password_digest = generate_password_hash(password)
    set_user_password_digest(cursor, email, password_digest)


def invalid_token_response():
    return make_response(
        {"message": "The submitted token is invalid"}, HTTPStatus.BAD_REQUEST
    )


def set_user_password_digest(cursor, email, password_digest):
    cursor.execute(
        f"update users set password_digest = '{password_digest}' where email = '{email}'"
    )


def token_is_expired(token_create_date):
    token_expired = (datetime.utcnow() - token_create_date).total_seconds() > 900
    return token_expired


def reset_token_validation(cursor, token):
    try:
        validate_token(cursor, token)
        return make_response({"message": "Token is valid"}, HTTPStatus.OK)
    except InvalidTokenError:
        return invalid_token_response()


def validate_token(cursor, token) -> str:
    try:
        token_data = check_reset_token(cursor, token)
    except TokenNotFoundError:
        raise InvalidTokenError
    email = token_data.get("email")
    if token_is_expired(token_create_date=token_data.get("create_date")):
        delete_reset_token(cursor, email, token)
        raise InvalidTokenError
    return email
