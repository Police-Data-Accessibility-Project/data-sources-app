from http import HTTPStatus

from flask import Response, make_response, jsonify
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    create_refresh_token, decode_token,
)
from sqlalchemy.orm.loading import get_from_identity
from werkzeug.security import check_password_hash

from database_client.database_client import DatabaseClient
from middleware.access_logic import AccessInfo
from middleware.primary_resource_logic.user_queries import UserRequestDTO
from middleware.schema_and_dto_logic.primary_resource_schemas.refresh_session_schemas import RefreshSessionRequestDTO


def try_logging_in(db_client: DatabaseClient, dto: UserRequestDTO) -> Response:
    """
    Tries to log in a user.

    :param db_client: DatabaseClient object.
    :param email: User's email.
    :param password: User's password.
    :return: A response object with a message and status code.
    """
    user_info = db_client.get_user_info(dto.email)
    if not check_password_hash(user_info.password_digest, dto.password):
        return unauthorized_response("Invalid email or password")
    return login_response(user_info)


def unauthorized_response(msg: str = "Unauthorized") -> Response:
    """
    Creates a response object for an unauthorized request.

    :return: A response object with a message and status code.
    """
    return make_response({"message": msg}, HTTPStatus.UNAUTHORIZED)


def login_response(
        user_info: DatabaseClient.UserInfo,
        message: str = "Successfully logged in"
) -> Response:
    """
    Creates a response object for a successful login.

    :param user_info: The user's information.
    :return: A response object with a message and status code.
    """
    access_token = create_access_token(identity=user_info.email)
    refresh_token = create_refresh_token(identity=user_info.email)
    return make_response(
        jsonify(
            message=message,
            access_token=access_token,
            refresh_token=refresh_token,
        ),
        HTTPStatus.OK,
    )

def access_and_refresh_token_response(
    email: str,
    message: str,
) -> Response:
    access_token = create_access_token(identity=email)
    refresh_token = create_refresh_token(identity=email)
    return make_response(
        jsonify(
            message=message,
            access_token=access_token,
            refresh_token=refresh_token,
        ),
        HTTPStatus.OK,
    )

def refresh_session(
        db_client: DatabaseClient,
        access_info: AccessInfo,
        dto: RefreshSessionRequestDTO
) -> Response:
    """
    Requires an active flask context and a valid JWT passed in the Authorization header
    :return:
    """
    decoded_refresh_token = decode_token(dto.refresh_token)
    decoded_email = decoded_refresh_token["sub"]
    if access_info.user_email != decoded_email:
        return make_response(
            {"message": "Invalid refresh token"}, HTTPStatus.UNAUTHORIZED
        )
    return access_and_refresh_token_response(
        email=decoded_email,
        message="Successfully refreshed session token.",
    )
