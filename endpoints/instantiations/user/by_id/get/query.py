from typing import final, Any

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from db.models.implementations.core.user.core import User
from db.queries.builder.core import QueryBuilderBase

@final
class GetUserByIdQueryBuilder(QueryBuilderBase):

    def __init__(self, user_id: int) -> None:
        super().__init__()
        self.user_id = user_id

    def run(self) -> dict[str, Any]:
        query = (
            select(User)
            .where(User.id == self.user_id)
            .options(
                selectinload(User.external_accounts),
                selectinload(User.capacities),
                selectinload(User.recent_searches),
                selectinload(User.followed_locations),
                selectinload(User.data_requests),
                selectinload(User.permissions),
            )
        )