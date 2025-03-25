from datetime import timedelta, timezone, datetime
from http import HTTPStatus
from typing import Optional

from flask import Response, make_response, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from werkzeug.security import check_password_hash

from database_client.database_client import DatabaseClient
from middleware.SimpleJWT import JWTPurpose, SimpleJWT
from middleware.access_logic import AccessInfoPrimary, RefreshAccessInfo
from middleware.exceptions import UserNotFoundError
from middleware.primary_resource_logic.user_queries import UserRequestDTO
from middleware.schema_and_dto_logic.primary_resource_schemas.refresh_session_schemas import (
    RefreshSessionRequestDTO,
)


class JWTAccessRefreshTokens:

    def __init__(self, email: str):
        db_client = DatabaseClient()
        user_id = db_client.get_user_id(email)
        permissions = db_client.get_user_permissions(user_id)
        other_claims = {
            "user_id": user_id,
            "user_email": email,
            "permissions": [permission.value for permission in permissions],
        }
        identity = str(user_id)
        simple_jwt = SimpleJWT(
            sub=identity,
            exp=self.get_expiry(),
            purpose=JWTPurpose.STANDARD_ACCESS_TOKEN,
            **other_claims
        )

        # Expiration of access token and refresh
        #  provided in JWT_ACCESS_TOKEN_EXPIRES and
        #  JWT_REFRESH_TOKEN_EXPIRES variables in `app.py`
        self.access_token = simple_jwt.encode()
        self.refresh_token = create_refresh_token(
            identity=identity, additional_claims={"email": email}
        )

    @staticmethod
    def get_expiry():
        return (datetime.now(tz=timezone.utc) + timedelta(minutes=15)).timestamp()


INVALID_MESSAGE = "Invalid email or password"


def try_logging_in(db_client: DatabaseClient, dto: UserRequestDTO) -> Response:
    """
    Tries to log in a user.

    :param db_client: DatabaseClient object.
    :param email: User's email.
    :param password: User's password.
    :return: A response object with a message and status code.
    """
    user_info = get_user_info(db_client, dto)
    if user_info is None:
        if db_client.pending_user_exists(dto.email):
            return unauthorized_response("Email not verified.")
        return unauthorized_response(INVALID_MESSAGE)
    valid_password_hash = check_password_hash(
        pwhash=user_info.password_digest, password=dto.password
    )
    if not valid_password_hash:
        return unauthorized_response(INVALID_MESSAGE)
    return login_response(user_info)


def get_user_info(db_client, dto) -> Optional[DatabaseClient.UserInfo]:
    try:
        return db_client.get_user_info(dto.email)
    except UserNotFoundError:
        return None


def unauthorized_response(msg: str = "Unauthorized") -> Response:
    """
    Creates a response object for an unauthorized request.

    :return: A response object with a message and status code.
    """
    return make_response({"message": msg}, HTTPStatus.UNAUTHORIZED)


def login_response(
    user_info: DatabaseClient.UserInfo, message: str = "Successfully logged in"
) -> Response:
    """
    Creates a response object for a successful login.

    :param user_info: The user's information.
    :return: A response object with a message and status code.
    """
    return access_and_refresh_token_response(
        email=user_info.email,
        message=message,
    )


def access_and_refresh_token_response(
    email: str,
    message: str,
) -> Response:
    jwt_tokens = JWTAccessRefreshTokens(email)
    return make_response(
        jsonify(
            message=message,
            access_token=jwt_tokens.access_token,
            refresh_token=jwt_tokens.refresh_token,
        ),
        HTTPStatus.OK,
    )


def refresh_session(
    db_client: DatabaseClient,
    access_info: RefreshAccessInfo,
) -> Response:
    """
    Requires an active flask context and a valid JWT passed in the Authorization header
    :return:
    """
    return handle_refresh_session_responses(access_info.user_email)


def handle_refresh_session_responses(decoded_email):
    return access_and_refresh_token_response(
        email=decoded_email,
        message="Successfully refreshed session token.",
    )
