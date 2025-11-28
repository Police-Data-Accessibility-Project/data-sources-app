from db.queries.helpers import run_query_builder
from endpoints.v3.permissions.user._shared.get_permission import GetPermissionIDByNameQueryBuilder
from endpoints.v3.permissions.user.add.query import AddUserPermissionQueryBuilder
from middleware.enums import PermissionsEnum
from middleware.schema_and_dto.dtos.common_dtos import MessageDTO


def add_user_permission_wrapper(
    user_id: int,
    permission: PermissionsEnum
) -> MessageDTO:
    permission_id: int = run_query_builder(
        GetPermissionIDByNameQueryBuilder(permission=permission)
    )
    run_query_builder(
        AddUserPermissionQueryBuilder(
            user_id=user_id,
            permission_id=permission_id,
        )
    )
    return MessageDTO(
        message="Permission successfully added."
    )
