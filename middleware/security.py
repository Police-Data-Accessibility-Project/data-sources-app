from http import HTTPStatus
from flask import request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from flask_restx import abort

from database_client.database_client import DatabaseClient
from middleware.enums import PermissionsEnum
from middleware.initialize_psycopg_connection import initialize_psycopg_connection
from typing import Optional

from middleware.permissions_logic import PermissionsManager


def get_api_key_from_header() -> str:
    """
    Validates the API key and checks if the user has the required role to access a specific endpoint.
    :return:
    """
    check_for_header_with_authorization_key()
    api_key = extract_api_key_from_header()
    return api_key


def extract_api_key_from_header():
    authorization_header = get_authorization_header()
    check_for_properly_formatted_authorization_header(authorization_header)
    api_key = authorization_header[1]
    return api_key


def get_authorization_header() -> list[str]:
    authorization_header = request.headers["Authorization"].split(" ")
    return authorization_header


def check_for_properly_formatted_authorization_header(authorization_header):
    if len(authorization_header) != 2 or authorization_header[0] != "Basic":
        abort(
            code=HTTPStatus.BAD_REQUEST,
            message="Please provide a properly formatted Basic token and API key"
        )


def check_for_header_with_authorization_key():
    if not request.headers or "Authorization" not in request.headers:
        abort(
            code=HTTPStatus.BAD_REQUEST,
            message="Please provide an 'Authorization' key in the request header",
        )


def get_db_client() -> DatabaseClient:
    return DatabaseClient()


def check_api_key_associated_with_user(db_client: DatabaseClient, api_key: str) -> None:
    user_id = db_client.get_user_by_api_key(api_key)
    if user_id is None:
        abort(HTTPStatus.UNAUTHORIZED, "Invalid API Key")

def check_api_key() -> None:
    api_key = get_api_key_from_header()
    db_client = get_db_client()
    check_api_key_associated_with_user(db_client, api_key)

def check_permissions(
    permission: PermissionsEnum
) -> None:
    """
    Checks if a user has a permission.
    Must be within flask context.

    :param permission: Permission to check.
    :return: True if the user has the permission, False otherwise.
    """
    verify_jwt_in_request()
    user_email = get_jwt_identity()
    db_client = get_db_client()
    pm = PermissionsManager(db_client=db_client, user_email=user_email)
    if not pm.has_permission(permission):
        abort(
            code=HTTPStatus.FORBIDDEN,
            message="You do not have permission to access this endpoint"
        )
