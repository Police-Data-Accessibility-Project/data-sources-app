from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from werkzeug.exceptions import Forbidden

from db.client.core import DatabaseClient
from middleware.enums import PermissionsEnum
from middleware.primary_resource_logic.permissions import PermissionsManager


def check_permissions(permission: PermissionsEnum) -> None:
    """
    Checks if a user has a permission.
    Must be within flask context.

    :param permission: Permission to check.
    :return: True if the user has the permission, False otherwise.
    """
    verify_jwt_in_request()
    identity = get_jwt_identity()
    email = identity["user_email"]
    db_client = DatabaseClient()
    pm = PermissionsManager(db_client=db_client, user_email=email)
    if not pm.has_permission(permission):
        raise Forbidden("You do not have permission to access this endpoint")
