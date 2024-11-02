import uuid
from http import HTTPStatus

from flask import Response, make_response, jsonify
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    create_refresh_token,
)
from werkzeug.security import check_password_hash

from database_client.database_client import DatabaseClient
from middleware.primary_resource_logic.user_queries import UserRequestDTO


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


def generate_api_key() -> str:
    return uuid.uuid4().hex


def create_api_key_for_user(db_client: DatabaseClient, dto: UserRequestDTO) -> Response:
    """
    Tries to log in a user. If successful, generates API key

    :param db_client: A DatabaseClient object.
    :param email: User's email.
    :param password: User's password.
    :return: A response object with a message and status code.
    """
    user_data = db_client.get_user_info(dto.email)

    if check_password_hash(user_data.password_digest, dto.password):
        api_key = generate_api_key()
        db_client.update_user_api_key(user_id=user_data.id, api_key=api_key)
        payload = {"api_key": api_key}
        return make_response(payload, HTTPStatus.OK)

    return make_response(
        {"message": "Invalid email or password"}, HTTPStatus.UNAUTHORIZED
    )


def refresh_session() -> Response:
    """
    Requires an active flask context and a valid JWT passed in the Authorization header
    :return:
    """
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return make_response(
        {"message": "Successfully refreshed session token", "data": access_token},
        HTTPStatus.OK,
    )
