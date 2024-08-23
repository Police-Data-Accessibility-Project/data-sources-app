from dataclasses import dataclass
from datetime import datetime
from http import HTTPStatus

from flask import Response, make_response
from typing import Dict, Union

from werkzeug.security import generate_password_hash

from database_client.database_client import DatabaseClient
from middleware.exceptions import TokenNotFoundError
from middleware.login_queries import generate_api_key
from middleware.user_queries import user_check_email
from middleware.webhook_logic import send_password_reset_link


class InvalidTokenError(Exception):
    pass


@dataclass
class RequestResetPasswordRequest:
    email: str
    token: str


def request_reset_password(db_client: DatabaseClient, email) -> Response:
    """
    Generates a reset token and sends an email to the user with instructions on how to reset their password.
    :param cursor:
    :param email:
    :return:
    """
    user_check_email(db_client, email)
    token = generate_api_key()
    db_client.add_reset_token(email, token)
    send_password_reset_link(email, token)
    return make_response(
        {
            "message": "An email has been sent to your email address with a link to reset your password. It will be valid for 15 minutes.",
            "token": token,
        },
        HTTPStatus.OK,
    )


def reset_password(
    db_client: DatabaseClient, dto: RequestResetPasswordRequest
) -> Response:
    """
    Resets a user's password if the provided token is valid and not expired.
    :param db_client:
    :param token:
    :param password:
    :return:
    """
    try:
        email = validate_token(db_client, dto.token)
    except InvalidTokenError:
        return invalid_token_response()
    set_user_password(db_client, email, dto.token)
    return make_response({"message": "Successfully updated password"}, HTTPStatus.OK)


def set_user_password(db_client: DatabaseClient, email, password):
    password_digest = generate_password_hash(password)
    db_client.set_user_password_digest(email, password_digest)


def invalid_token_response():
    return make_response(
        {"message": "The submitted token is invalid"}, HTTPStatus.BAD_REQUEST
    )


def token_is_expired(token_create_date):
    token_expired = (datetime.utcnow() - token_create_date).total_seconds() > 900
    return token_expired


def reset_token_validation(db_client: DatabaseClient, token):
    try:
        validate_token(db_client, token)
        return make_response({"message": "Token is valid"}, HTTPStatus.OK)
    except InvalidTokenError:
        return invalid_token_response()


def validate_token(db_client: DatabaseClient, token) -> str:
    token_data = db_client.get_reset_token_info(token)
    if token_data is None:
        raise InvalidTokenError
    email = token_data.email
    if token_is_expired(token_create_date=token_data.create_date):
        db_client.delete_reset_token(email, token)
        raise InvalidTokenError
    return email
