from http import HTTPStatus
from flask import request
from flask_restx import abort

from database_client.database_client import DatabaseClient
from middleware.enums import PermissionsEnum
from middleware.initialize_psycopg2_connection import initialize_psycopg2_connection
from typing import Optional

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


def check_user_permission(db_client: DatabaseClient, user_id: str, permission: Optional[PermissionsEnum]):
    if permission is None:
        return
    user_permissions = db_client.get_user_permissions(user_id)
    if permission in user_permissions:
        return
    abort(HTTPStatus.FORBIDDEN, "You do not have permission to access this endpoint")

def get_db_client() -> DatabaseClient:
    psycopg2_connection = initialize_psycopg2_connection()
    return DatabaseClient(psycopg2_connection.cursor())

def get_user_id_from_database(db_client: DatabaseClient, api_key: str) -> str:
    user_id = db_client.get_user_by_api_key(api_key)
    if user_id is None:
        abort(HTTPStatus.UNAUTHORIZED, "Invalid API Key")
    return user_id

def check_api_key(permission: PermissionsEnum) -> bool:
    api_key = get_api_key_from_header()
    db_client = get_db_client()
    user_id = get_user_id_from_database(db_client, api_key)
    check_user_permission(db_client, user_id, permission)


