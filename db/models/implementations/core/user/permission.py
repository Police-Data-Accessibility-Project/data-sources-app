from sqlalchemy import ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.base import Base
from db.models.mixins import UserIDMixin
from middleware.enums import Relations


class UserPermission(Base, UserIDMixin):
    __tablename__ = Relations.USER_PERMISSIONS.value

    permission_id: Mapped[int] = mapped_column(ForeignKey("public.permissions.id"))

    __table_args__ = (
        PrimaryKeyConstraint("user_id", "permission_id", name="user_permission_pkey"),
        {"schema": "public"},
    )
