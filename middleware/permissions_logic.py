from dataclasses import dataclass
from enum import Enum
from http import HTTPStatus
from typing import Type

from flask import Response, make_response
from flask_jwt_extended import get_jwt_identity
from flask_restx import abort

from database_client.database_client import DatabaseClient
from database_client.helper_functions import get_db_client
from middleware.custom_exceptions import UserNotFoundError
from middleware.enums import PermissionsEnum, PermissionsActionEnum
from utilities.common import get_valid_enum_value

@dataclass
class PermissionsRequest:
    user_email: str
    permission: str
    action: str


class PermissionsManager:
    """
    Class that manages user permissions.
    """

    def __init__(self, db_client: DatabaseClient, user_email: str):
        try:
            user_info = db_client.get_user_info(user_email)
        except UserNotFoundError:
            abort(HTTPStatus.NOT_FOUND, "User not found")
            return
        self.db_client = db_client
        self.user_email = user_email

        self.permissions = self.db_client.get_user_permissions(user_info.id)

    def has_permission(self, permission: PermissionsEnum) -> bool:
        return permission in self.permissions

    def get_user_permissions(self) -> Response:
        permissions_list = [permission.value for permission in self.permissions]
        return make_response(
            permissions_list,
            HTTPStatus.OK
        )

    def add_user_permission(self, permission: PermissionsEnum) -> Response:
        if permission in self.permissions:
            return make_response(
                f"Permission {permission.value} already exists for user",
                HTTPStatus.CONFLICT
            )

        self.db_client.add_user_permission(self.user_email, permission)
        return make_response(
            "Permission added",
            HTTPStatus.OK
        )

    def remove_user_permission(self, permission: PermissionsEnum) -> Response:
        if permission not in self.permissions:
            return make_response(
                f"Permission {permission.value} does not exist for user. Cannot remove.",
                HTTPStatus.CONFLICT
            )
        self.db_client.remove_user_permission(self.user_email, permission)
        return make_response(
            "Permission removed",
            HTTPStatus.OK
        )

def manage_user_permissions(
        db_client: DatabaseClient,
        user_email: str,
        method: str,
        *args,
        **kwargs
) -> Response:
    # Create an instance of PermissionsManager
    permissions_manager = PermissionsManager(db_client, user_email)

    # Call the provided method on the PermissionsManager instance
    if hasattr(permissions_manager, method):
        method_to_call = getattr(permissions_manager, method)
        return method_to_call(*args, **kwargs)
    else:
        raise AttributeError(f"Method {method} does not exist in PermissionsManager")

def update_permissions_wrapper(
    db_client: DatabaseClient,
    dto: PermissionsRequest,
) -> Response:
    action = get_valid_enum_value(PermissionsActionEnum, dto.action)
    permission = get_valid_enum_value(PermissionsEnum, dto.permission)
    return manage_user_permissions(
        db_client=db_client,
        user_email=dto.user_email,
        method=f"{action.value}_user_permission",
        permission=permission
    )


def get_user_permissions(user_email: str) -> list[PermissionsEnum]:
    db_client = get_db_client()
    pm = PermissionsManager(db_client, user_email)
    return pm.permissions
