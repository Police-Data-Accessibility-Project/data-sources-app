from flask import Response
from marshmallow import Schema, fields
from pydantic import BaseModel
from werkzeug.exceptions import Conflict
from werkzeug.security import generate_password_hash

from db.client.core import DatabaseClient
from middleware.common_response_formatting import message_response
from middleware.exceptions import UserNotFoundError, DuplicateUserError
from utilities.enums import SourceMappingEnum


class UserRequestSchema(Schema):
    email = fields.Str(
        required=True,
        metadata={
            "description": "The email of the user",
            "source": SourceMappingEnum.JSON,
        },
    )
    password = fields.Str(
        required=True,
        metadata={
            "description": "The password of the user",
            "source": SourceMappingEnum.JSON,
        },
    )


class UserRequestDTO(BaseModel):
    email: str
    password: str


def user_check_email(db_client: DatabaseClient, email: str) -> int:
    """
    Checks if a user with the given email exists in the database, raising an error if not.

    :param db_client: A DatabaseClient object.
    :param email: The email address to check against the users in the database.
    :return: A dictionary with the user's ID if found, otherwise an error message.
    """
    user_id = db_client.get_user_id(email)
    if user_id is None:
        raise UserNotFoundError(email)
    return user_id


def user_post_results(db_client: DatabaseClient, dto: UserRequestDTO) -> Response:
    """
    Creates a new user with the provided email and password.

    :param db_client: A DatabaseClient object.
    :param email: The email address of the new user.
    :param password: The password for the new user.
    """
    password_digest = generate_password_hash(dto.password)
    try:
        db_client.create_new_user(dto.email, password_digest)
    except DuplicateUserError:
        raise Conflict(
            f"User with email {dto.email} already exists.",
        )

    return message_response("Successfully added user.")
