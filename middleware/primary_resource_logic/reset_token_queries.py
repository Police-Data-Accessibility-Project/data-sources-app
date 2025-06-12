from datetime import datetime, timedelta, timezone
from http import HTTPStatus

from flask import Response, make_response
from werkzeug.exceptions import BadRequest, Unauthorized

from werkzeug.security import generate_password_hash, check_password_hash

from db.client import DatabaseClient
from middleware.security.jwt.core import SimpleJWT
from middleware.security.jwt.enums import JWTPurpose
from middleware.security.access_info.password_reset import PasswordResetTokenAccessInfo
from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.common_response_formatting import message_response
from middleware.exceptions import UserNotFoundError
from middleware.flask_response_manager import FlaskResponseManager
from middleware.primary_resource_logic.api_key import generate_token
from middleware.primary_resource_logic.user_queries import user_check_email
from middleware.schema_and_dto.dtos.reset_password.request import (
    RequestResetPasswordRequestDTO,
)
from middleware.schema_and_dto.dtos.reset_password.reset import ResetPasswordDTO
from middleware.schema_and_dto.dtos.user_profile import (
    UserPutDTO,
)
from middleware.webhook_logic import send_password_reset_link


class InvalidTokenError(Exception):
    pass


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
        user_id=user_id,
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
    return make_response({"message": "Successfully updated password"})


def validate_user_ids_match(user_id: int, token_user_id: int):
    if user_id != token_user_id:
        raise BadRequest("Invalid token.")


def change_password_wrapper(
    db_client: DatabaseClient,
    dto: UserPutDTO,
    access_info: AccessInfoPrimary,
):
    user_id = access_info.user_id

    # Check if old password is valid
    # get old password digest
    db_password_digest = db_client.get_password_digest(user_id=user_id)
    matches = check_password_hash(pwhash=db_password_digest, password=dto.old_password)
    if not matches:
        raise Unauthorized("Incorrect existing password.")
    set_user_password(db_client=db_client, user_id=user_id, password=dto.new_password)
    return message_response(
        message="Successfully updated password.",
    )


def set_user_password(db_client: DatabaseClient, user_id: int, password: str):
    password_digest = generate_password_hash(password)
    db_client.update_user_password_digest(
        user_id=user_id, password_digest=password_digest
    )


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
        raise BadRequest("Token not found.")

    user_id = token_data.user_id
    if token_is_expired(token_create_date=token_data.create_date):
        db_client.delete_reset_token(user_id, token)
        raise BadRequest("Token is expired.")

    return user_id
