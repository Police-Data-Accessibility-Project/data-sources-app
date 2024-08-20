from http import HTTPStatus
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from flask_restx import abort

from database_client.database_client import DatabaseClient
from database_client.helper_functions import get_db_client
from middleware.access_logic import InvalidAPIKeyException, InvalidAuthorizationHeaderException, \
    get_api_key_from_request_header
from middleware.enums import PermissionsEnum
from middleware.permissions_logic import PermissionsManager

INVALID_API_KEY_MESSAGE = "Please provide an API key in the request header in the 'Authorization' key with the format 'Basic <api_key>'"


def check_api_key_associated_with_user(db_client: DatabaseClient, api_key: str) -> None:
    user_identifiers = db_client.get_user_by_api_key(api_key)
    if user_identifiers is None:
        abort(HTTPStatus.UNAUTHORIZED, "Invalid API Key")

def check_api_key() -> None:
    try:
        api_key = get_api_key_from_request_header()
        db_client = get_db_client()
        check_api_key_associated_with_user(db_client, api_key)
    except (InvalidAPIKeyException, InvalidAuthorizationHeaderException):
        abort(
            code=HTTPStatus.UNAUTHORIZED,
            message=INVALID_API_KEY_MESSAGE
        )



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
