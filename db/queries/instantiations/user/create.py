from typing import final, override

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from db.enums import UserCapacityEnum
from db.models.implementations.core.user.capacity import UserCapacity
from db.models.implementations.core.user.core import User
from db.queries.builder.core import QueryBuilderBase
from middleware.exceptions import DuplicateDisplayNameError, DuplicateUserError
from middleware.schema_and_dto.dtos.user.display_name import (
    default_display_name_for_user_id,
)


@final
class CreateNewUserQueryBuilder(QueryBuilderBase):
    def __init__(
        self,
        email: str,
        password_digest: str,
        capacities: list[UserCapacityEnum] | None = None,
        display_name: str | None = None,
    ):
        super().__init__()
        self.email = email
        self.password_digest = password_digest
        self.capacities = capacities if capacities else []
        self.display_name = display_name

    @override
    def run(self) -> int:
        if self.display_name is not None:
            self._raise_if_display_name_taken(self.display_name)

        # We need the user.id before we can fall back to the id-based default
        # display name, so insert a placeholder, flush, then update.
        placeholder_display_name = self.display_name or "__pending__"
        user = User(
            email=self.email,
            password_digest=self.password_digest,
            display_name=placeholder_display_name,
        )
        self.session.add(user)
        try:
            self.session.flush()
        except IntegrityError:
            raise DuplicateUserError

        if self.display_name is None:
            user.display_name = default_display_name_for_user_id(user.id)
            try:
                self.session.flush()
            except IntegrityError:
                raise DuplicateDisplayNameError

        self._add_user_capacities(user_id=user.id)
        return user.id

    def _raise_if_display_name_taken(self, display_name: str) -> None:
        existing = self.session.execute(
            select(User.id).where(
                func.lower(User.display_name) == display_name.lower()
            )
        ).scalar_one_or_none()
        if existing is not None:
            raise DuplicateDisplayNameError

    def _add_user_capacities(self, user_id: int):
        for capacity in self.capacities:
            self.session.add(UserCapacity(user_id=user_id, capacity=capacity.value))
