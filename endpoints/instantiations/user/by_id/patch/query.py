from typing import override, final

from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import IntegrityError

from db.models.implementations.core.user.capacity import UserCapacity
from db.models.implementations.core.user.core import User
from db.queries.builder.core import QueryBuilderBase
from endpoints.instantiations.user.by_id.patch.dto import UserPatchDTO
from middleware.exceptions import DuplicateDisplayNameError


@final
class UserPatchQueryBuilder(QueryBuilderBase):
    def __init__(self, dto: UserPatchDTO, user_id: int):
        super().__init__()
        self.dto = dto
        self.user_id = user_id

    @override
    def run(self) -> None:
        if self.dto.capacities is not None:
            self._delete_existing_user_capacities()
            self._add_user_capacities()
        if self.dto.display_name is not None:
            self._update_display_name(self.dto.display_name)

    def _add_user_capacities(self):
        for capacity in self.dto.capacities or []:
            self.session.add(
                UserCapacity(user_id=self.user_id, capacity=capacity.value)
            )

    def _delete_existing_user_capacities(self):
        query = delete(UserCapacity).where(UserCapacity.user_id == self.user_id)
        _ = self.session.execute(query)

    def _update_display_name(self, display_name: str) -> None:
        # Pre-check uniqueness against other users so we can produce a
        # descriptive error before triggering an integrity violation.
        existing = self.session.execute(
            select(User.id).where(
                func.lower(User.display_name) == display_name.lower(),
                User.id != self.user_id,
            )
        ).scalar_one_or_none()
        if existing is not None:
            raise DuplicateDisplayNameError

        try:
            self.session.execute(
                update(User)
                .where(User.id == self.user_id)
                .values(display_name=display_name)
            )
            self.session.flush()
        except IntegrityError:
            raise DuplicateDisplayNameError
