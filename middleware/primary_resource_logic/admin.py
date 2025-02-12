# middleware/primary_resource_logic/admin.py
from flask import Response
from werkzeug.security import generate_password_hash

from database_client.DTOs import UserInfoNonSensitive
from middleware.access_logic import AccessInfoPrimary
from middleware.db_client import DatabaseClient

from middleware.common_response_formatting import created_id_response
from middleware.dynamic_request_logic.supporting_classes import MiddlewareParameters
from middleware.enums import Relations
from middleware.primary_resource_logic.util import (
    create_entry,
    delete_entry,
    get_entries,
    get_entry_by_id,
    update_entry,
)

from middleware.flask_response_manager import FlaskResponseManager
from middleware.schema_and_dto_logic.primary_resource_dtos.admin_dtos import (
    AdminUserPostDTO,
    AdminUserPutDTO,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.admin_schemas import AdminUserBaseSchema

ADMIN_POST_MIDDLEWARE_PARAMETERS = MiddlewareParameters(
    entry_name="admin_user",
    relation=Relations.USERS.value,
    db_client_method=DatabaseClient.create_admin_user,
)


ADMIN_PUT_MIDDLEWARE_PARAMETERS = MiddlewareParameters(
    entry_name="admin_user",
    relation=Relations.USERS.value,
    db_client_method=DatabaseClient.update_admin_user,
)


def get_users_admin(
        db_client: DatabaseClient,
        access_info: AccessInfoPrimary
) -> list[dict]:
    # Return database client method
    pass


def get_user_by_id_admin(
        db_client: DatabaseClient,
        access_info: AccessInfoPrimary,
        user_id: str
) -> Response:
    # Return database client method
    user_info: UserInfoNonSensitive = db_client.get_user_info_by_id(user_id)

    user_permissions = db_client.get_user_permissions(user_id)

    return FlaskResponseManager.make_response({
        "id": user_info.id,
        "created_at": user_info.created_at,
        "updated_at": user_info.updated_at,
        "email": user_info.email,
        "permissions": [permission.value for permission in user_permissions]
    })


def create_admin_user(
        db_client: DatabaseClient,
        access_info: AccessInfoPrimary,
        dto: AdminUserPostDTO
) -> Response:
    # Hash password
    password_digest = generate_password_hash(dto.password)

    # Apply database client method for user and get id
    user_id = db_client.create_new_user(
        email=dto.email,
        password_digest=password_digest
    )

    # Apply database client method for permissions
    for permission in dto.permissions:
        db_client.add_user_permission(user_id, permission)

    # Return response with id
    return created_id_response(
        new_id=str(user_id), message="User created."
    )


def update_admin_user(db_client: DatabaseClient, access_info: AccessInfoPrimary, admin_user_id: str, dto: AdminUserPutDTO) -> dict:
    # Hash password
    pass

    # Apply database client method

    # Return response