# middleware/primary_resource_logic/admin.py
from flask import Response
from werkzeug.security import generate_password_hash

from db.DTOs import UsersWithPermissions
from db.client import DatabaseClient

from middleware.common_response_formatting import created_id_response

from middleware.flask_response_manager import FlaskResponseManager
from middleware.schema_and_dto.dtos.common.base import (
    GetManyBaseDTO,
    GetByIDBaseDTO,
)
from middleware.schema_and_dto.dtos.admin.put import AdminUserPutDTO
from middleware.schema_and_dto.dtos.admin.post import AdminUserPostDTO


def get_users_admin(db_client: DatabaseClient, dto: GetManyBaseDTO) -> Response:
    # Return database client method
    results: list[UsersWithPermissions] = db_client.get_users(page=dto.page)
    return FlaskResponseManager.make_response(
        {
            "message": "Returning users",
            "data": [user.model_dump(mode="json") for user in results],
            "metadata": {"count": len(results)},
        }
    )


def create_admin_user(db_client: DatabaseClient, dto: AdminUserPostDTO) -> Response:
    # Hash password
    password_digest = generate_password_hash(dto.password)

    # Apply database client method for user and get id
    user_id = db_client.create_new_user(
        email=dto.email, password_digest=password_digest
    )

    # Apply database client method for permissions
    for permission in dto.permissions:
        db_client.add_user_permission(user_id, permission)

    # Return response with id
    return created_id_response(new_id=str(user_id), message="User created.")


def update_user_password(
    db_client: DatabaseClient, user_id: int, dto: AdminUserPutDTO
) -> Response:
    # Hash password
    password_digest = generate_password_hash(dto.password)

    # Apply database client method
    db_client.update_user_password_digest(
        user_id=user_id, password_digest=password_digest
    )

    # Return response
    return FlaskResponseManager.make_response({"message": "User updated."})


def delete_user(db_client: DatabaseClient, dto: GetByIDBaseDTO) -> Response:
    # Apply database client method
    db_client.delete_user(user_id=int(dto.resource_id))

    # Return response
    return FlaskResponseManager.make_response({"message": "User deleted."})
