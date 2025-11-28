from typing import Sequence

from sqlalchemy import select, RowMapping

from db.models.implementations.core.permission import Permission
from db.models.implementations.core.user.permission import UserPermission
from db.queries.builder.core import QueryBuilderBase
from endpoints.v3.permissions.get.response import GetPermissionListResponse, PermissionDescriptionMapping


class GetUserPermissionsQueryBuilder(QueryBuilderBase):

    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id

    def run(self) -> GetPermissionListResponse:
        query = (
            select(
                Permission.permission_name.label("permission"),
                Permission.description,
            )
            .join(
                UserPermission,
                UserPermission.permission_id == Permission.id,
            )
            .where(
                UserPermission.user_id == self.user_id,
            )
        )
        mappings: Sequence[RowMapping] = self.mappings(query)
        return GetPermissionListResponse(
            mappings=[
                PermissionDescriptionMapping(**mapping)
                for mapping in mappings
            ]
        )