from typing import override, final

from sqlalchemy import delete

from db.models.implementations.core.user.capacity import UserCapacity
from db.queries.builder.core import QueryBuilderBase
from endpoints.instantiations.user.by_id.patch.dto import UserPatchDTO

@final
class UserPatchQueryBuilder(QueryBuilderBase):

    def __init__(self, dto: UserPatchDTO, user_id: int):
        super().__init__()
        self.dto = dto
        self.user_id = user_id

    @override
    def run(self) -> None:

        self._delete_existing_user_capacities()
        self._add_user_capacities()

    def _add_user_capacities(self):
        for capacity in self.dto.capacities:
            self.session.add(UserCapacity(user_id=self.user_id, capacity=capacity.value))

    def _delete_existing_user_capacities(self):
        query = delete(UserCapacity).where(UserCapacity.user_id == self.user_id)
        _ = self.session.execute(query)

