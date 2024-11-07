from http import HTTPStatus
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from flask_restx import abort

from database_client.helper_functions import get_db_client
from middleware.enums import PermissionsEnum
from middleware.primary_resource_logic.permissions_logic import PermissionsManager


def check_permissions(permission: PermissionsEnum) -> None:
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
            message="You do not have permission to access this endpoint",
        )
