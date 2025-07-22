from typing import final, override

from sqlalchemy.exc import IntegrityError

from db.enums import UserCapacityEnum
from db.models.implementations.core.user.capacity import UserCapacity
from db.models.implementations.core.user.core import User
from db.queries.builder.core import QueryBuilderBase
from middleware.exceptions import DuplicateUserError


@final
class CreateNewUserQueryBuilder(QueryBuilderBase):
    def __init__(
        self,
        email: str,
        password_digest: str,
        capacities: list[UserCapacityEnum] | None = None,
    ):
        super().__init__()
        self.email = email
        self.password_digest = password_digest
        self.capacities = capacities if capacities else []

    @override
    def run(self) -> int:
        user = User(email=self.email, password_digest=self.password_digest)
        self.session.add(user)
        try:
            self.session.flush()
        except IntegrityError:
            raise DuplicateUserError
        self._add_user_capacities(user_id=user.id)
        return user.id

    def _add_user_capacities(self, user_id: int):
        for capacity in self.capacities:
            self.session.add(UserCapacity(user_id=user_id, capacity=capacity.value))
