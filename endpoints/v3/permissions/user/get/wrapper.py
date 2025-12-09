from db.queries.helpers import run_query_builder
from endpoints.v3.permissions.get.response import GetPermissionListResponse
from endpoints.v3.permissions.user.get.query import GetUserPermissionsQueryBuilder


def get_user_permissions_wrapper(
    user_id: int,
) -> GetPermissionListResponse:
    return run_query_builder(GetUserPermissionsQueryBuilder(user_id=user_id))
