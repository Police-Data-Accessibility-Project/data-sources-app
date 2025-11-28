from flask import Response, make_response
from werkzeug.exceptions import BadRequest, Conflict

from db.client.core import DatabaseClient
from middleware.common_response_formatting import message_response
from middleware.enums import PermissionsEnum
from middleware.exceptions import UserNotFoundError


class PermissionsManager:
    """
    Class that manages user permissions.
    """

    def __init__(self, db_client: DatabaseClient, user_email: str):
        try:
            user_info = db_client.get_user_info(user_email)
        except UserNotFoundError:
            raise BadRequest("User not found.")
        self.db_client = db_client
        self.user_email = user_email
        self.user_id = user_info.id
        self.permissions = self.db_client.get_user_permissions(user_info.id)

    def has_permission(self, permission: PermissionsEnum) -> bool:
        return permission in self.permissions

    def get_user_permissions(self) -> Response:
        permissions_list = [permission.value for permission in self.permissions]
        return make_response(permissions_list)

    def add_user_permission(self, permission: PermissionsEnum) -> Response:
        if permission in self.permissions:
            raise Conflict(f"Permission {permission.value} already exists for user")

        self.db_client.add_user_permission(self.user_id, permission)
        return message_response("Permission added")

    def remove_user_permission(self, permission: PermissionsEnum) -> Response:
        if permission not in self.permissions:
            raise Conflict(
                f"Permission {permission.value} does not exist for user. Cannot remove."
            )

        self.db_client.remove_user_permission(self.user_id, permission)
        return message_response("Permission removed")



