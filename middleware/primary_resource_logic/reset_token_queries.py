from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from http import HTTPStatus

from flask import Response, make_response

from marshmallow import Schema, fields
from werkzeug.security import generate_password_hash

from database_client.database_client import DatabaseClient
from middleware.SimpleJWT import SimpleJWT, JWTPurpose
from middleware.access_logic import PasswordResetTokenAccessInfo
from middleware.common_response_formatting import message_response
from middleware.exceptions import UserNotFoundError
from middleware.flask_response_manager import FlaskResponseManager
from middleware.primary_resource_logic.api_key_logic import generate_token
from middleware.primary_resource_logic.user_queries import user_check_email
from middleware.schema_and_dto_logic.primary_resource_dtos.request_reset_password_dtos import (
    RequestResetPasswordRequestDTO,
)
from middleware.webhook_logic import send_password_reset_link
from utilities.enums import SourceMappingEnum


class InvalidTokenError(Exception):
    pass


@dataclass
class RequestResetPasswordRequest:
    email: str
    token: str


class ResetPasswordRequestSchema(Schema):
    email = fields.Str(
        required=True,
        metadata={
            "description": "The email of the user",
            "source": SourceMappingEnum.JSON,
        },
    )
    token = fields.Str(
        required=True,
        metadata={
            "description": "The token of the user",
            "source": SourceMappingEnum.JSON,
        },
    )


class ResetPasswordSchema(Schema):
    password = fields.Str(
        required=True,
        metadata={
            "description": "The new password of the user",
            "source": SourceMappingEnum.JSON,
        },
    )


@dataclass
class ResetPasswordDTO:
    password: str


def request_reset_password_response():
    return message_response(
        message="If the email is valid, an email has been sent to the user with instructions on how to reset their password.",
    )


def request_reset_password(
    db_client: DatabaseClient, dto: RequestResetPasswordRequestDTO
) -> Response:
    """
    Generates a reset token and sends an email to the user with instructions on how to reset their password.
    :param cursor:
    :param email:
    :return:
    """
    email = dto.email
    try:
        user_id = user_check_email(db_client, email)
    except UserNotFoundError:
        return request_reset_password_response()

    token = generate_token()
    db_client.add_reset_token(user_id=user_id, token=token)
    jwt_token = SimpleJWT(
        sub={
            "user_email": email,
            "user_id": user_id,
            "token": token,
        },
        exp=(datetime.now(tz=timezone.utc) + timedelta(minutes=15)).timestamp(),
        purpose=JWTPurpose.PASSWORD_RESET,
    )
    send_password_reset_link(email=email, token=jwt_token.encode())
    return request_reset_password_response()


def reset_password(
    db_client: DatabaseClient,
    dto: ResetPasswordDTO,
    access_info: PasswordResetTokenAccessInfo,
) -> Response:
    """
    Resets a user's password if the provided token is valid and not expired.
    :param db_client:
    :param token:
    :param password:
    :return:
    """
    user_id = validate_token(db_client, access_info.reset_token)
    validate_user_ids_match(access_info.user_id, user_id)

    set_user_password(db_client=db_client, user_id=user_id, password=dto.password)
    return FlaskResponseManager.make_response(
        {"message": "Successfully updated password"}, HTTPStatus.OK
    )


def validate_user_ids_match(user_id: int, token_user_id: int):
    if user_id != token_user_id:
        FlaskResponseManager.abort(
            code=HTTPStatus.BAD_REQUEST, message="Invalid token."
        )


def set_user_password(db_client: DatabaseClient, user_id: int, password: str):
    password_digest = generate_password_hash(password)
    db_client.set_user_password_digest(user_id=user_id, password_digest=password_digest)


def invalid_token_response():
    return make_response({"message": "Token is invalid"}, HTTPStatus.BAD_REQUEST)


def token_is_expired(token_create_date):
    token_expired = (datetime.utcnow() - token_create_date).total_seconds() > 900
    return token_expired


def reset_token_validation(db_client: DatabaseClient, token):
    validate_token(db_client, token)
    return make_response({"message": "Token is valid"}, HTTPStatus.OK)


def validate_token(db_client: DatabaseClient, token) -> int:
    token_data = db_client.get_reset_token_info(token)
    if token_data is None:
        FlaskResponseManager.abort(
            message="Token not found.", code=HTTPStatus.BAD_REQUEST
        )
    user_id = token_data.user_id
    if token_is_expired(token_create_date=token_data.create_date):
        db_client.delete_reset_token(user_id, token)
        FlaskResponseManager.abort(
            message="Token is expired.", code=HTTPStatus.BAD_REQUEST
        )
    return user_id
