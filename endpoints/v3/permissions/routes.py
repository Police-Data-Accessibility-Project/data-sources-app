from fastapi import APIRouter, Depends

from db.queries.helpers import run_query_builder
from endpoints.v3.permissions.get.query import GetPermissionMappingsQueryBuilder
from endpoints.v3.permissions.get.response import GetPermissionListResponse
from endpoints.v3.permissions.user._shared.request import UpdatePermissionRequest
from endpoints.v3.permissions.user.add.wrapper import add_user_permission_wrapper
from endpoints.v3.permissions.user.get.wrapper import get_user_permissions_wrapper
from endpoints.v3.permissions.user.remove.wrapper import remove_user_permission_wrapper
from middleware.schema_and_dto.dtos.common_dtos import MessageDTO
from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.security.auth.fastapi import (
    access_with_user_create_update,
    access_with_read_all_user_info,
)

permission_router = APIRouter(prefix="/permission", tags=["Permission"])


@permission_router.get("")
def get_permission_list() -> GetPermissionListResponse:
    return run_query_builder(GetPermissionMappingsQueryBuilder())


@permission_router.get("/user/{user_id}")
def get_user_permissions(
    user_id: int,
    access_info: AccessInfoPrimary = Depends(access_with_read_all_user_info),
) -> GetPermissionListResponse:
    return get_user_permissions_wrapper(user_id=user_id)


@permission_router.post("/user/{user_id}/add")
def add_user_permission(
    user_id: int,
    request: UpdatePermissionRequest,
    access_info: AccessInfoPrimary = Depends(access_with_user_create_update),
) -> MessageDTO:
    return add_user_permission_wrapper(user_id=user_id, permission=request.permission)


@permission_router.post("/user/{user_id}/remove")
def remove_user_permission(
    user_id: int,
    request: UpdatePermissionRequest,
    access_info: AccessInfoPrimary = Depends(access_with_user_create_update),
) -> MessageDTO:
    return remove_user_permission_wrapper(
        user_id=user_id, permission=request.permission
    )
