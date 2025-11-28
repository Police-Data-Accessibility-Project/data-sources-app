from sqlalchemy import select

from db.models.implementations.core.permission import Permission
from db.queries.builder.core import QueryBuilderBase
from middleware.enums import PermissionsEnum


class GetPermissionIDByNameQueryBuilder(QueryBuilderBase):

    def __init__(self, permission: PermissionsEnum):
        super().__init__()
        self.permission = permission

    def run(self) -> int:
        query = (
            select(
                Permission.id,
            )
            .where(
                Permission.permission_name == self.permission.value,
            )
        )

        return self.scalar(query)