from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from db.models.mixins import UserIDMixin
from db.models.templates.standard import StandardBase
from middleware.enums import Relations


class UserPermission(StandardBase, UserIDMixin):
    __tablename__ = Relations.USER_PERMISSIONS.value

    permission_id: Mapped[int] = mapped_column(ForeignKey("public.permissions.id"))
