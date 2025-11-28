from db.queries.helpers import run_query_builder
from endpoints.v3.permissions.user._shared.get_permission import GetPermissionIDByNameQueryBuilder
from endpoints.v3.permissions.user.remove.query import RemoveUserPermissionQueryBuilder
from middleware.enums import PermissionsEnum
from middleware.schema_and_dto.dtos.common_dtos import MessageDTO


def remove_user_permission_wrapper(
    permission: PermissionsEnum,
    user_id: int
) -> MessageDTO:
    permission_id: int = run_query_builder(
        GetPermissionIDByNameQueryBuilder(permission=permission)
    )
    run_query_builder(
        RemoveUserPermissionQueryBuilder(
            user_id=user_id,
            permission_id=permission_id,
        )
    )
    return MessageDTO(
        message="Permission successfully removed."
    )