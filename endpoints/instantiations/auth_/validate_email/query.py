from typing import final, override

from sqlalchemy import func, select, delete
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest, Conflict

from db.models.implementations.core.user.capacity import UserCapacity
from db.models.implementations.core.user.core import User
from db.models.implementations.core.user.pending import PendingUser
from db.queries.builder.core import QueryBuilderBase
from middleware.exceptions import DuplicateDisplayNameError, DuplicateUserError
from middleware.schema_and_dto.dtos.user.display_name import (
    DISPLAY_NAME_DUPLICATE_MESSAGE,
    default_display_name_for_user_id,
)


@final
class ValidateEmailQueryBuilder(QueryBuilderBase):
    def __init__(self, validation_token: str):
        super().__init__()
        self.validation_token = validation_token

    def _add_user_capacities(self, capacities: list[str], user_id: int):
        for capacity in capacities:
            self.session.add(UserCapacity(user_id=user_id, capacity=capacity))

    def get_pending_user(self) -> PendingUser | None:
        query = select(
            PendingUser.email,
            PendingUser.password_digest,
            PendingUser.capacities,
            PendingUser.display_name,
        ).where(PendingUser.validation_token == self.validation_token)
        return self.session.execute(query).one_or_none()

    def _is_display_name_taken(self, display_name: str) -> bool:
        existing = self.session.execute(
            select(User.id).where(
                func.lower(User.display_name) == display_name.lower()
            )
        ).scalar_one_or_none()
        return existing is not None

    def _delete_pending_user(self):
        query = delete(PendingUser).where(
            PendingUser.validation_token == self.validation_token
        )
        self.session.execute(query)

    def _create_new_user(self, pending_user: PendingUser) -> None:
        requested_display_name: str | None = pending_user.display_name
        if requested_display_name is not None and self._is_display_name_taken(
            requested_display_name
        ):
            raise DuplicateDisplayNameError

        # Insert with a placeholder display_name so we can later substitute
        # the user id if no name was provided at signup.
        placeholder_display_name = requested_display_name or "__pending__"
        user = User(
            email=pending_user.email,
            password_digest=pending_user.password_digest,
            display_name=placeholder_display_name,
        )
        self.session.add(user)
        try:
            self.session.flush()
        except IntegrityError:
            raise DuplicateUserError

        if requested_display_name is None:
            user.display_name = default_display_name_for_user_id(user.id)
            try:
                self.session.flush()
            except IntegrityError:
                raise DuplicateDisplayNameError

        self._add_user_capacities(capacities=pending_user.capacities, user_id=user.id)
        self._delete_pending_user()

    @override
    def run(self) -> str:
        pending_user = self.get_pending_user()
        if pending_user is None:
            raise BadRequest("Invalid validation token.")

        try:
            self._create_new_user(pending_user)
        except DuplicateDisplayNameError:
            raise Conflict(DISPLAY_NAME_DUPLICATE_MESSAGE)
        return pending_user.email
