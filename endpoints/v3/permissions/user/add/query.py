from typing import Any

from db.models.implementations.core.user.permission import UserPermission
from db.queries.builder.core import QueryBuilderBase


class AddUserPermissionQueryBuilder(QueryBuilderBase):
    def __init__(self, user_id: int, permission_id: int):
        super().__init__()
        self.user_id = user_id
        self.permission_id = permission_id

    def run(self) -> Any:
        up = UserPermission(
            user_id=self.user_id,
            permission_id=self.permission_id,
        )
        self.session.add(up)
