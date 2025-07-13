from typing import final, override

from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest

from db.enums import UserCapacityEnum
from db.models.implementations.core.user.capacity import UserCapacity
from db.models.implementations.core.user.core import User
from db.models.implementations.core.user.pending import PendingUser
from db.queries.builder.core import QueryBuilderBase
from middleware.exceptions import DuplicateUserError


@final
class ValidateEmailQueryBuilder(QueryBuilderBase):

    def __init__(self, validation_token: str):
        super().__init__()
        self.validation_token = validation_token

    def _add_user_capacities(
        self,
        capacities: list[UserCapacityEnum],
        user_id: int
    ):
        for capacity in capacities:
            self.session.add(
                UserCapacity(
                    user_id=user_id,
                    capacity=capacity.value
                )
            )


    def get_pending_user(self) -> PendingUser | None:
        query = select(
            PendingUser.email,
            PendingUser.password_digest,
            PendingUser.capacities
        ).where(
            PendingUser.validation_token == self.validation_token
        )
        return self.session.execute(query).one_or_none()

    def _delete_pending_user(self):
        query = delete(PendingUser).where(PendingUser.validation_token == self.validation_token)
        self.session.execute(query)

    def _create_new_user(self, pending_user: PendingUser) -> None:
        user = User(
            email=pending_user.email,
            password_digest=pending_user.password_digest
        )
        self.session.add(user)
        try:
            self.session.flush()
        except IntegrityError:
            raise DuplicateUserError
        self._add_user_capacities(
            capacities=pending_user.capacities,
            user_id=user.id
        )
        self._delete_pending_user()

    @override
    def run(self) -> str:
        pending_user = self.get_pending_user()
        if pending_user is None:
            raise BadRequest("Invalid validation token.")

        self._create_new_user(pending_user)
        return pending_user.email

